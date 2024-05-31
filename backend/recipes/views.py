from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import viewsets, mixins
from rest_framework import filters
from rest_framework.response import Response

from recipes.serializers import (IngredientsSerializer, TagsSerializer,
                                 RecipeSerializer, RecipePostPatchSerializer)
from recipes.models import Ingredient, Tag, Recipe
from recipes.services import is_valid_uuid

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('^name',)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipePostPatchSerializer
        return super().get_serializer_class()

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @action(['get'], url_path='get-link', detail=True)
    def get_link(self, request, *args, **kwargs):
        uri = request.build_absolute_uri('/s/')
        recipe_pk = self.kwargs.get('pk')
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        return Response({'short-link': uri + str(recipe.unique_uuid)})

    @action(['get'], detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer(raise_exception=True)
        return Response(serializer.data)


class GetRecipeByLinkViewSet(viewsets.GenericViewSet,
                             mixins.RetrieveModelMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def retrieve(self, request, *args, **kwargs):
        recipe = self.kwargs.get('pk')
        if is_valid_uuid(recipe):
            uuid = Recipe.objects.get(unique_uuid=recipe)
            serializer = self.get_serializer(uuid)
            return Response(serializer.data)
