from django.contrib.auth import get_user_model
from django.core.validators import (MinValueValidator,
                                    RegexValidator,
                                    MaxValueValidator)
from django.db import models

User = get_user_model()

LENGTH_OF_STR = 20
MIN_VALUE = 1
MAX_VALUE = 32767


class Tag(models.Model):
    """Модель тегов для рецептов."""

    name = models.CharField(
        'Тег',
        max_length=200,
        unique=True)
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Поле должно содержать HEX-код выбранного цвета.')])
    slug = models.SlugField(
        'Слаг тега',
        unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']

    def __str__(self):
        return self.name[:LENGTH_OF_STR]

    def clean(self):
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        self.color = self.color.strip().lower()
        return super().clean()


class Ingredient(models.Model):
    """Модель ингредиентов для рецептов."""

    name = models.CharField(
        'Ингредиент',
        max_length=200)
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=20)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient')]

    def __str__(self) -> str:
        return f'{self.name[:LENGTH_OF_STR]} {self.measurement_unit}'

    def clean(self):
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        super().clean()


class Recipe(models.Model):
    """Модель для рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes')
    name = models.CharField(
        'Название',
        max_length=200)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/')
    text = models.TextField(
        'Описание')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (мин)',
        default=0,
        validators=(
            MinValueValidator(
                MIN_VALUE,
                message='Ваше блюдо уже готово!'),
            MaxValueValidator(
                MAX_VALUE,
                message='Очень долго ждать...')))

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:LENGTH_OF_STR]

    def clean(self):
        self.name = self.name.capitalize()
        return super().clean()


class RecipeIngredient(models.Model):
    """Промежуточная модель для связей
    между рецептами и ингредиентами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredient')
    amount = models.PositiveSmallIntegerField(
        'Количество',
        default=0,
        validators=(
            MinValueValidator(
                MIN_VALUE,
                message='Кажется, вы забыли добавить ингредиенты.'),
            MaxValueValidator(
                MAX_VALUE,
                message='Вы переборщили с количеством ингредиентов.')))

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient')]

    def __str__(self) -> str:
        return (f'{self.recipe.name[:LENGTH_OF_STR]}: '
                f'{self.ingredient.name[:LENGTH_OF_STR]} - '
                f'({self.amount} '
                f'{self.ingredient.measurement_unit})')


class UserList(models.Model):
    """Абстрактная модель для Favorites и ShoppingCart."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)s_user')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)s_recipe')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name[:LENGTH_OF_STR]}'


class Favorites(UserList):
    """Модель для избранных рецептов пользователей."""

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe')]


class ShoppingCart(UserList):
    """Модель для рецептов в списке покупок пользователей"""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart')]
