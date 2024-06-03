from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe


class RecipeFilterSet(FilterSet):
    tags = filters.CharFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='recipes_shopping_cart__is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='recipes_shopping_cart__is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


