# Generated by Django 4.2.13 on 2024-05-20 15:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follows',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follows', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
        migrations.AddConstraint(
            model_name='follows',
            constraint=models.UniqueConstraint(fields=('user', 'following'), name='unique_user_follower'),
        ),
        migrations.AddConstraint(
            model_name='follows',
            constraint=models.CheckConstraint(check=models.Q(('user', models.F('following')), _negated=True), name='user_cannot_follow_themselves'),
        ),
    ]
