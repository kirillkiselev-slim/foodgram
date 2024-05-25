from rest_framework import viewsets
from rest_framework import filters


from recipes.serializers import (IngredientsSerializer, TagsSerializer,
                                 RecipesSerializer)
from recipes.models import Ingredients, Tags, Recipes


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    pagination_class = None
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('^name',)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    pagination_class = None
    serializer_class = TagsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipesSerializer
    queryset = Recipes.objects.all()

    def get_user(self):
        return self.request.user


