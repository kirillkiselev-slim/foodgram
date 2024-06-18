from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import action, api_view
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Sum, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from api.serializers import (IngredientsSerializer, TagsSerializer,
                             RecipeSerializer, RecipePostPatchSerializer,
                             ShoppingCartSerializer, FavoriteSerializer)
from recipes.models import (Ingredient, Tag, Recipe,
                            ShoppingCart, IngredientRecipe,
                            Favorite)
from recipes.services import write_ingredients_to_csv
from api.filters import RecipeFilterSet, IngredientsFilterSet
from api.permissions import (AuthorOrAdminOnly, ReadOrAdminOnly,
                             RecipeAuthorOrAdminOnly)
from djoser.views import UserViewSet
from api.serializers import FollowSerializer
from users.models import Follows

User = get_user_model()


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
        elif self.action in {'partial_update', 'destroy'}:
            self.permission_classes = (RecipeAuthorOrAdminOnly,)
        return super().get_permissions()

    def get_user(self):
        return self.request.user

    def serializer_favorite_or_shopping_cart(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer

    def get_shopping_cart(self):
        return get_object_or_404(ShoppingCart, user=self.get_user(),
                                 recipe=self.get_object())

    def get_favorite(self):
        return get_object_or_404(Favorite, user=self.get_user(),
                                 recipe=self.get_object())

    def get_serializer_class(self):
        if self.action in {'create', 'partial_update'}:
            return RecipePostPatchSerializer
        if self.action in {'favorite', 'delete_favorite'}:
            return FavoriteSerializer
        if self.action in {'shopping_cart', 'delete_shopping_cart'}:
            return ShoppingCartSerializer
        return super().get_serializer_class()

    @action(('get',), url_path='get-link', detail=True)
    def get_link(self, request, *args, **kwargs):
        uri = request.build_absolute_uri('/s/')
        return Response({'short-link': f'{uri}'
                                       f'{self.get_object().unique_uuid}'})

    @action(('post',), detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        serializer = self.serializer_favorite_or_shopping_cart()
        ShoppingCart.objects.update_or_create(
            recipe=self.get_object(), user=self.get_user(),
            defaults={'is_in_shopping_cart': True})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, *args, **kwargs):
        self.serializer_favorite_or_shopping_cart()
        shopping_cart = self.get_shopping_cart()
        shopping_cart.is_in_shopping_cart = False
        shopping_cart.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('get',), detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        user = request.user
        ingredients = IngredientRecipe.objects.filter(
            recipe__shoppingcart_recipes__user=user,
            recipe__shoppingcart_recipes__is_in_shopping_cart=True).values(
            ingredient_name=F('ingredient__name'),
            ingredient_unit=F('ingredient__measurement_unit')).annotate(
            Sum('amount'))
        if not ingredients:
            return Response({'shopping_cart': 'Корзина пуста'})
        return write_ingredients_to_csv(ingredients)

    @action(('post',), detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        serializer = self.serializer_favorite_or_shopping_cart()
        Favorite.objects.update_or_create(
            recipe=self.get_object(), user=self.get_user(),
            defaults={'is_favorited': True})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, *args, **kwargs):
        self.serializer_favorite_or_shopping_cart()
        favorite = self.get_favorite()
        favorite.is_favorited = False
        favorite.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(('GET',))
def get_recipe(request, *args, **kwargs):
    recipe = kwargs.get('recipe')
    recipe = get_object_or_404(Recipe, unique_uuid=recipe)
    uri = request.build_absolute_uri(f'/recipes/{recipe.id}/')
    return HttpResponseRedirect(uri)


class UserFoodgramViewSet(UserViewSet):

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = (ReadOrAdminOnly,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in {'subscribe', 'subscriptions'}:
            return FollowSerializer
        return super().get_serializer_class()

    @action(('patch', 'delete', 'put'), detail=True,
            permission_classes=(AuthorOrAdminOnly,))
    def avatar(self, request, *args, **kwargs):
        user = self.request.user
        if request.method in {'PATCH', 'PUT'}:
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'avatar': serializer.data.get('avatar')})
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('post', 'delete'), detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        follower_pk = self.request.parser_context.get('kwargs').get('id')
        follower = get_object_or_404(User, pk=follower_pk)
        if request.method == 'POST':
            serializer = self.get_serializer(user, data={})
            serializer.is_valid(raise_exception=True)
            Follows.objects.create(user=user, following=follower)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        follow = get_object_or_404(Follows, user=user, following=follower)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('get',), detail=False, permission_classes=(AuthorOrAdminOnly,))
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        queryset = User.objects.filter(followers__user=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
