from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(max_length=254, blank=False, null=False,
                              unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=False,
                               default='default.png')
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)

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

    class Meta:
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
