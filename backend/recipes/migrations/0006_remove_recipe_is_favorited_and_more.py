# Generated by Django 4.2.13 on 2024-05-30 19:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_recipe_is_favorited_recipe_is_in_shopping_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='is_favorited',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='is_in_shopping_cart',
        ),
    ]
