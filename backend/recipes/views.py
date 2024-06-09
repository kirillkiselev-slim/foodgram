from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny

from recipes.serializers import (IngredientsSerializer, TagsSerializer,
                                 RecipeSerializer, RecipePostPatchSerializer,
                                 ShoppingCartSerializer)
from recipes.models import (Ingredient, Tag, Recipe,
                            ShoppingCart, IngredientRecipe)
from recipes.services import is_valid_uuid, write_ingredients_to_csv
from api.filters import RecipeFilterSet, IngredientsFilterSet
from api.permissions import AuthorOrAdminOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientsSerializer
    filter_backends = (IngredientsFilterSet,)
    search_fields = ('^name',)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (IsAuthenticated,)
        elif self.action == 'list':
            self.permission_classes = (AllowAny,)
        elif self.action in ('partial_update', 'destroy',):
            self.permission_classes = (AuthorOrAdminOnly,)
        elif self.action in ('shopping_cart', 'favorite',
                             'download_shopping_cart'):
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_recipe(self):
        recipe_pk = self.kwargs.get('pk')
        return get_object_or_404(Recipe, pk=recipe_pk)

    def get_user(self):
        return self.request.user

    def serializer_favorite_and_shopping_cart(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer

    def get_shopping_cart(self):
        return ShoppingCart.objects.get(user=self.get_user(),
                                        recipe=self.get_recipe())

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipePostPatchSerializer
        elif self.action in ('shopping_cart', 'favorite'):
            return ShoppingCartSerializer
        return super().get_serializer_class()

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @action(['get'], url_path='get-link', detail=True)
    def get_link(self, request, *args, **kwargs):
        uri = request.build_absolute_uri('/s/')
        return Response({'short-link': uri + str(self.get_recipe()
                                                 .unique_uuid)})

    @action(['post', 'delete'], detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        serializer = self.serializer_favorite_and_shopping_cart()
        if request.method == 'POST':
            ShoppingCart.objects.update_or_create(
                recipe=self.get_recipe(), user=self.get_user(),
                defaults={'is_in_shopping_cart': True})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        shopping_cart = self.get_shopping_cart()
        shopping_cart.is_in_shopping_cart = False
        shopping_cart.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(
            user=user, is_in_shopping_cart=True)
        recipes = [recipe.recipe.pk for recipe in shopping_cart]
        ingredients = IngredientRecipe.objects.filter(
            recipe__in=recipes).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            Sum('amount'))
        if not ingredients:
            return Response({'shopping_cart': 'Корзина пуста'})
        return write_ingredients_to_csv(ingredients)

    @action(['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        serializer = self.serializer_favorite_and_shopping_cart()
        if request.method == 'POST':
            ShoppingCart.objects.update_or_create(
                recipe=self.get_recipe(), user=self.get_user(),
                defaults={'is_favorited': True})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        shopping_cart = self.get_shopping_cart()
        shopping_cart.is_favorited = False
        shopping_cart.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        return Response({'uuid': 'Неправильного формата UUID.'})
