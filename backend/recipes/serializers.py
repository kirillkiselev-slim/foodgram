from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import CurrentUserDefault
from api.constants import (UNIQUE_TAGS, UNIQUE_INGREDIENTS,
                           ALREADY_IN_SHOPPING_CART, NOT_IN_SHOPPING_CART,
                           NOT_IN_FAVORED, ALREADY_IN_FAVORITED)

from recipes.models import Ingredient, Tag, Recipe, IngredientRecipe, ShoppingCart
from api.serializers import Base64ImageField
from users.serializers import ProfileSerializer

User = get_user_model()


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    author = ProfileSerializer(read_only=True)
    tags = TagsSerializer(many=True)
    ingredients = IngredientsSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_request(self):
        return self.context.get('request')

    def get_user(self):
        return self.get_request().user

    def get_is_favorited(self, obj):
        if self.get_user().is_anonymous:
            return False
        is_favorited = obj.recipes_shopping_cart.filter(
            user=self.get_user(), recipe=obj)
        if not is_favorited.exists():
            return False
        return is_favorited.first().is_favorited

    def get_is_in_shopping_cart(self, obj):
        if self.get_user().is_anonymous:
            return False
        is_in_shopping_cart = obj.recipes_shopping_cart.filter(
            user=self.get_user(), recipe=obj)
        if not is_in_shopping_cart.exists():
            return False
        return is_in_shopping_cart.first().is_in_shopping_cart

    def to_representation(self, instance):
        data = super().to_representation(instance)
        ingredients = data.get('ingredients', None)
        ingredients_recipes = instance.recipe_ingredients.all()
        ingredient_amounts = {ir.ingredient.id: ir.amount for
                              ir in ingredients_recipes}
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            ingredient['amount'] = ingredient_amounts.get(ingredient_id, 0)
        return data


class RecipePostPatchSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, write_only=True,
                                              queryset=Tag.objects.all(),
                                              required=True, allow_empty=False)
    author = serializers.HiddenField(default=CurrentUserDefault())
    ingredients = serializers.ListField(required=True, allow_empty=False)

    class Meta(RecipeSerializer.Meta):
        pass

    def validate(self, recipe_data):
        tags = recipe_data.get('tags')
        ingredients = recipe_data.get('ingredients')

        if tags is not None:
            if len(set(tags)) != len(tags):
                raise ValidationError(UNIQUE_TAGS)
        if ingredients is not None:
            ingredients_ids = [ingredient.get('id') for ingredient in ingredients]
            if len(set(ingredients_ids)) != len(ingredients):
                raise ValidationError(UNIQUE_INGREDIENTS)
        return recipe_data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            ingredient_id = get_object_or_404(Ingredient,
                                              pk=ingredient_id)
            amount = ingredient.get('amount')
            IngredientRecipe.objects.create(ingredient=ingredient_id,
                                            recipe=recipe, amount=amount)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            for ingredient in ingredients:
                ingredient_id = ingredient.get('id')
                amount = ingredient.get('amount')
                ingredient_instance = get_object_or_404(
                    Ingredient, pk=ingredient_id)
                recipe_ingredient, _ = instance.recipe_ingredients.get_or_create(
                    ingredient=ingredient_instance)
                recipe_ingredient.amount = amount
                recipe_ingredient.save()

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def get_request(self):
        return self.context.get('request')

    def get_user(self):
        return self.get_request().user

    def get_recipe(self):
        return self.get_request().parser_context.get('kwargs').get('pk')

    def validate(self, shopping_cart_data):
        recipe = get_object_or_404(Recipe, pk=self.get_recipe())
        path = self.get_request().path
        if 'shopping_cart' in path:
            if self.get_request().method == 'POST':
                if recipe.recipes_shopping_cart.filter(
                        recipe=recipe, user=self.get_user(),
                        is_in_shopping_cart=True):
                    raise ValidationError(ALREADY_IN_SHOPPING_CART)

            elif self.get_request().method == 'DELETE':
                if not recipe.recipes_shopping_cart.filter(
                        recipe=recipe, user=self.get_user(),
                        is_in_shopping_cart=True):
                    raise ValidationError(NOT_IN_SHOPPING_CART)
        else:
            if self.get_request().method == 'POST':
                if recipe.recipes_shopping_cart.filter(
                        recipe=recipe, user=self.get_user(),
                        is_favorited=True):
                    raise ValidationError(ALREADY_IN_FAVORITED)

            elif self.get_request().method == 'DELETE':
                if not recipe.recipes_shopping_cart.filter(
                        recipe=recipe, user=self.get_user(),
                        is_favorited=True):
                    raise ValidationError(NOT_IN_FAVORED)
        return shopping_cart_data

    def to_representation(self, instance):
        pk = self.get_recipe()
        recipe = Recipe.objects.get(pk=pk)
        data = {
            'id': recipe.id,
            'name': recipe.name,
            'image': self.get_request().build_absolute_uri(recipe.image.url),
            'cooking_time': recipe.cooking_time
        }
        return data
