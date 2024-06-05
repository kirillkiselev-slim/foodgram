from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(max_length=254, blank=False, null=False,
                              unique=True, verbose_name='Имейл')
    avatar = models.ImageField(upload_to='avatars/', null=False,
                               default='default.png', verbose_name='Аватар')
    first_name = models.CharField(max_length=150, blank=False, null=False,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=False, null=False,
                                 verbose_name='Фамилия')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.email


class Follows(models.Model):
    user = models.ForeignKey(CustomUser, related_name='follows',
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    following = models.ForeignKey(CustomUser, related_name='followers',
                                  on_delete=models.CASCADE,
                                  verbose_name='Подписчик')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_user_follower'
            ),
            models.CheckConstraint(
                check=~Q(user=models.F('following')),
                name='user_cannot_follow_themselves',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
