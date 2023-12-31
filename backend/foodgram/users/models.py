from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Переопределение базовой модели User."""

    email = models.EmailField('Электронная почта',
                              max_length=254,
                              unique=True)
    username = models.CharField('Имя пользователя',
                                max_length=150,
                                unique=True)
    first_name = models.CharField('Имя',
                                  max_length=150)
    last_name = models.CharField('Фамилия',
                                 max_length=150)
    password = models.CharField('Пароль',
                                max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='unique_email_username'
            )
        ]
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок на автора."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
