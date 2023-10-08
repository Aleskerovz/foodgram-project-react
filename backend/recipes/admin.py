from django.contrib import admin
from django.forms import ValidationError
from django.forms import BaseInlineFormSet

from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class BaseAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class IngredientInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_ingredients = False
        for form in self.forms:
            if form.cleaned_data and not (
                    form.cleaned_data.get('DELETE', False)):
                has_ingredients = True
                break
        if not has_ingredients:
            raise ValidationError('Добавьте хотя бы один ингредиент')


class IngredientInline(admin.TabularInline):

    model = RecipeIngredient
    extra = 3
    formset = IngredientInlineFormSet


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    search_fields = ('name', 'color')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    list_display = ('pk', 'name', 'author', 'in_favorites')
    list_editable = ('name', 'author')
    list_filter = ('name', 'author__username', 'tags__name')
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = (IngredientInline,)
    empty_value_display = '-пусто-'

    def in_favorites(self, obj):
        return obj.shoppingcart_recipe.count()

    in_favorites.short_description = 'В избранном'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(BaseAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(Favorites)
class FavoriteAdmin(BaseAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(BaseAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
