from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'password',
        'first_name',
        'last_name']

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True)
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True)
    first_name = models.CharField(
        'Имя',
        max_length=150)
    last_name = models.CharField(
        'Фамилия',
        max_length=150)
    password = models.CharField(
        'Пароль',
        max_length=150)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='unique_email_username')]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки пользователя на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author')]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'Пользователь не может подписаться на самого себя.')
