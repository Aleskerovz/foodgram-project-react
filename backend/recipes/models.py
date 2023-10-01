from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тегов для рецептов."""

    name = models.CharField(
        'Тег',
        max_length=200,
        unique=True)
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        unique=True)
    slug = models.SlugField(
        'Слаг тега',
        unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


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
        return f'{self.name} {self.measurement_unit}'


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
    text = models.TextField('Описание')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
        blank=False)
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (мин)',
        validators=[
            MinValueValidator(
                1, message='Время должно быть больше 0!')])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_for_author')]

    def __str__(self):
        return self.name


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
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                1, message='Введите значение больше 0!')])

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient')]

    def __str__(self) -> str:
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - '
                f'({self.amount} '
                f'{self.ingredient.measurement_unit})')


class Favorites(models.Model):
    """Модель для избранных рецептов пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite_user')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Понравившиеся рецепты',
        related_name='favorite_recipe')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe')]

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'


class ShoppingCart(models.Model):
    """Модель для товаров в корзине покупок пользователей"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь списка корзины',
        related_name='shopping_user')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в корзине',
        related_name='shopping_recipe')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'В корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart')]

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'
