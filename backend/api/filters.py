from rest_framework.filters import SearchFilter

from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe


class RecipeFilterSet(FilterSet):
    tags = filters.CharFilter(method='filter_tags')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='recipes_shopping_cart__is_in_shopping_cart',
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        author = self.request.user
        if not author.is_authenticated:
            return queryset
        return queryset.filter(
            author=author, recipes_shopping_cart__is_favorited=True)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        author = self.request.user
        if not author.is_authenticated:
            return queryset
        return queryset.filter(
            author=author, recipes_shopping_cart__is_in_shopping_cart=True)

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()


class IngredientsFilterSet(SearchFilter):
    search_param = 'name'
