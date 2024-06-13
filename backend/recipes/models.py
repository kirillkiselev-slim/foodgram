import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import validate_slug, MinValueValidator
from django.db.models import Count

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False,
                            verbose_name='Название')
    measurement_unit = models.CharField(max_length=64,
                                        blank=False, null=False,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='Название')
    slug = models.SlugField(max_length=32, unique=True,
                            verbose_name='Слаг',
                            validators=(validate_slug,), default=None)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор', related_name='recipes')
    name = models.CharField(max_length=256, verbose_name='Название',
                            blank=False, null=False)
    image = models.ImageField(upload_to='recipes/', null=False, blank=False,
                              verbose_name='Фото')
    text = models.TextField(null=False, blank=False, verbose_name='Текст')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe')
    tags = models.ManyToManyField(Tag, related_name='tags',
                                  verbose_name='теги')
    cooking_time = models.PositiveSmallIntegerField(
        blank=False, null=False, verbose_name='Время приготовления',
        validators=[MinValueValidator(1,
                                      message='Время приготовления должно'
                                              ' быть больше или равно 1')])
    unique_uuid = models.UUIDField(
        primary_key=False, default=uuid.uuid4,
        editable=False, verbose_name='Уникальный uuid')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    @property
    def is_favorited_count(self):
        field = self.recipes_shopping_cart.aggregate(Count('is_favorited'))
        return field.get('is_favorited__count', 0)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, verbose_name='ингредиент',
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_recipes')
    recipe = models.ForeignKey(Recipe, verbose_name='рецепт',
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество', default=1,
        validators=[MinValueValidator(1,
                                      message='Кол-во должно быть '
                                              'больше или равно 1')]
    )

    class Meta:
        verbose_name = 'Рецепт-ингредиент'
        verbose_name_plural = 'Рецепты-ингредиенты'

    def __str__(self):
        return f'{self.ingredient}-{self.recipe}"'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_shopping_cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipes_shopping_cart',
                               verbose_name='Рецепт')
    is_in_shopping_cart = models.BooleanField(default=False,
                                              verbose_name='в корзине')
    is_favorited = models.BooleanField(default=False,
                                       verbose_name='в избранном')

    class Meta:
        ordering = ('user',)
        verbose_name = 'Корзина-избранное'
        verbose_name_plural = 'Корзина-избранное'
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='user-recipe')
        ]

    def __str__(self):
        return f'Корзина-избранное {self.user} с рецептом "{self.recipe}"'
