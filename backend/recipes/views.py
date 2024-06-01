from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import viewsets, mixins, status
from rest_framework import filters
from rest_framework.response import Response
from django.db.models import Sum

from recipes.serializers import (IngredientsSerializer, TagsSerializer,
                                 RecipeSerializer, RecipePostPatchSerializer,
                                 ShoppingCartSerializer)
from recipes.models import Ingredient, Tag, Recipe, ShoppingCart, IngredientRecipe
from recipes.services import is_valid_uuid, write_ingredients_to_csv

User = get_user_model()


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
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
        return super().get_serializer_class()

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @action(['get'], url_path='get-link', detail=True)
    def get_link(self, request, *args, **kwargs):
        uri = request.build_absolute_uri('/s/')
        recipe_pk = self.kwargs.get('pk')
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        return Response({'short-link': uri + str(recipe.unique_uuid)})

    @action(['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        recipe_pk = self.kwargs.get('pk')
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            ShoppingCart.objects.create(recipe=recipe, user=user,
                                        is_in_shopping_cart=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        ShoppingCart.objects.filter(recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        user = User.objects.get(username='k') # TODO fix it to request.user
        shopping_cart = ShoppingCart.objects.filter(
            user=user, is_in_shopping_cart=True)
        recipes = [recipe.recipe.pk for recipe in shopping_cart]
        print(recipes)
        ingredients = IngredientRecipe.objects.filter(
            recipe__in=recipes).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            Sum('amount'))
        return write_ingredients_to_csv(ingredients)


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




