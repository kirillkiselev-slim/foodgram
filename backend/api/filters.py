from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework.filters import SearchFilter
from django_filters.filters import CharFilter

from recipes.models import Recipe, Tag


class RecipeFilterSet(FilterSet):
    tags = CharFilter(method='filter_tags')
    is_favorited = filters.BooleanFilter(
        field_name='recipes_shopping_cart__is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='recipes_shopping_cart__is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()


class IngredientsFilterSet(SearchFilter):
    search_param = 'name'
