from django.db import models
from django.core.validators import validate_slug

from users.models import CustomUser


class Ingredients(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False,
                            verbose_name='Название',)
    measurement_unit = models.CharField(max_length=64,
                                        blank=False, null=False,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tags(models.Model):
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


class Recipes(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING,
                               verbose_name='Автор', related_name='recipes')
    name = models.CharField(max_length=256, verbose_name='Название',
                            blank=False, null=False)
    image = models.ImageField(upload_to='recipes/', null=False, blank=False)
    text = models.TextField(null=False, blank=False)
    ingredients = models.ManyToManyField(Ingredients,
                                         through='IngredientsRecipes')
    tags = models.ManyToManyField(Tags, through='TagsRecipes')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'"{self.name}" от {self.author}'


class IngredientsRecipes(models.Model):
    ingredient = models.ForeignKey(Ingredients, verbose_name='ингредиент',
                                   on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, verbose_name='рецепт',
                               on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Рецепт-ингредиент'
        verbose_name_plural = 'Рецепты-ингредиенты'

    def __str__(self):
        return f'{self.ingredient}-{self.recipe}"'


class TagsRecipes(models.Model):
    tag = models.ForeignKey(Tags, verbose_name='тег',
                            on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, verbose_name='рецепт',
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Рецепт-тег'
        verbose_name_plural = 'Рецепты-теги'

    def __str__(self):
        return f'{self.tag}-{self.recipe}'



