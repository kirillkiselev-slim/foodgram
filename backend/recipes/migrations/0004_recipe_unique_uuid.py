# Generated by Django 4.2.13 on 2024-05-29 20:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredientrecipe_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='unique_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
