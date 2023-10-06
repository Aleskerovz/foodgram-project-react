from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from users.models import Subscription, User
from .filters import IngredientFilter, RecipeFilter
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          SubscriptionsListSerializer, SubscriptionsSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                data=request.data,
                context={'request': request,
                         'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if Subscription.objects.filter(author=author, user=user).exists():
                Subscription.objects.get(author=author).delete()
                return Response('Вы успешно отписались от пользователя.',
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsListSerializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=request.data,
                                          context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not Favorites.objects.filter(user=request.user,
                                            recipe=recipe).exists():
                Favorites.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(Favorites, user=request.user,
                              recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(
                    user=request.user, recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(
                {'errors': 'Рецепт уже в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(
                ShoppingCart, user=request.user,
                recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .values_list('ingredient__name',
                         'ingredient__measurement_unit', 'amount'))
        shopping_list = []
        for name, measurement_unit, amount in ingredients:
            shopping_list.append(
                f'{name} - {amount} {measurement_unit} \n'
            )
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="shoplist.txt"'
        return response
