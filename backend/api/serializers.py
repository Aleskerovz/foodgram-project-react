import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import Subscription, User
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class Base64ImageField(serializers.ImageField):
    """Поле для сериализации изображений в формате base64.."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(UserSerializer):
    """Сериализатор для списка пользователей и профиля пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(
                user=self.context['request'].user, author=obj).exists())


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания нового пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для списка тегов и получения информации о теге."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для списка ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для списка ингредиентов с количеством для рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиента в рецепте."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов без ингредиентов."""

    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True,
        source='recipe_ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart',
                  'name', 'image', 'text',
                  'cooking_time')

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Favorites.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, изменения и удаления рецепта."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags',
                  'image', 'name', 'text',
                  'cooking_time', 'author')

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Выберите хотя бы один тег.')
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Выберите хотя бы один ингредиент.')
        return ingredients

    def validate(self, data):
        if self.context['request'].method != 'PATCH':
            if Recipe.objects.filter(
                name=data['name'], text=data['text']
            ).exists():
                raise serializers.ValidationError(
                    'Такой рецепт уже существует. '
                    'Измените название или описание.')
        return data

    def create_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            ingredient = get_object_or_404(
                Ingredient, pk=ingredient_data['id'])
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient,
                amount=ingredient_data['amount'])

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        if 'image' in validated_data:
            if instance.image:
                instance.image.delete()

        instance.image = validated_data['image']
        tags_data = validated_data.get('tags')
        ingredients_data = validated_data.get('ingredients')

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.create_ingredients(instance, ingredients_data)

        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeReadSerializer(instance,
                                    context={'request': request}).data


class BaseSubscriptionSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        author_obj = obj.author if hasattr(obj, 'author') else obj
        return Subscription.objects.filter(
            user=user,
            author=author_obj).exists()

    def get_recipes_count(self, obj):
        author_obj = obj.author if hasattr(obj, 'author') else obj
        return author_obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        author_obj = obj.author if hasattr(obj, 'author') else obj
        recipes = author_obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data


class SubscriptionsListSerializer(BaseSubscriptionSerializer):
    """Сериализатор для списка авторов, на которых подписан пользователь."""

    class Meta(BaseSubscriptionSerializer.Meta):
        model = User


class SubscriptionsSerializer(BaseSubscriptionSerializer):
    """Сериализатор для подписки на пользователя и отписки."""

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    class Meta(BaseSubscriptionSerializer.Meta):
        model = Subscription

    def validate(self, data):
        user = self.context.get('request').user
        author = self.context.get('author')
        if user.follower.filter(author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора!')
        if user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя!')
        return data


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и удаления рецептов в/из избранного."""

    class Meta:
        model = Favorites
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe,
            context={'request': request}).data

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        if Favorites.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.')
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и удаления рецептов в корзину покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe,
            context={'request': request}).data

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину.')
        return data
