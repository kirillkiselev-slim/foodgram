import base64

from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import CurrentUserDefault

from api.constants import (UNIQUE_TAGS, UNIQUE_INGREDIENTS,
                           ALREADY_IN_SHOPPING_CART, NOT_IN_SHOPPING_CART,
                           NOT_IN_FAVORED, ALREADY_IN_FAVORITED, USERS_RECIPE,
                           AMOUNT_ABOVE_ONE, NOT_NONE_INGREDIENTS,
                           CANNOT_FOLLOW_YOURSELF, ALREADY_FOLLOWS)
from recipes.models import Ingredient, Tag, Recipe, IngredientRecipe

User = get_user_model()


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, image_data):
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')

        return super().to_internal_value(image_data)


class ProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, user_data):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        return request.user.follows.filter(following=user_data.id).exists()


class FollowSerializer(ProfileSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(ProfileSerializer.Meta):
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name',)

    def follower_id(self):
        return int(self.context.get('view').kwargs.get('id'))

    def validate(self, follower_data):
        request = self.context.get('request')
        user = request.user
        follower_id = self.follower_id()
        if user.id == follower_id:
            raise serializers.ValidationError(CANNOT_FOLLOW_YOURSELF)
        if user.follows.filter(following=follower_id).exists():
            raise serializers.ValidationError(ALREADY_FOLLOWS)
        return follower_data

    def get_recipes(self, user_data):
        return Recipe.objects.filter(author=user_data)

    def get_recipes_count(self, user_data):
        return Recipe.objects.filter(author=user_data).count()

    def to_representation(self, instance):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', None)
        if request.method == 'POST':
            instance = get_object_or_404(User, pk=self.follower_id())
        data = super().to_representation(instance)
        data['recipes'] = [
            {'id': recipe.id, 'name': recipe.name,
             'image': request.build_absolute_uri(recipe.image.url),
             'cooking_time': recipe.cooking_time}
            for recipe in instance.recipes.all()
        ]
        if recipes_limit is not None:
            return data['recipes'][:int(recipes_limit)]
        return data


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

    def get_is_favorited(self, recipe_data):
        user = self.get_user()
        if not user.is_authenticated:
            return False
        is_favorited = recipe_data.recipes_shopping_cart.filter(
            user=user, recipe=recipe_data)
        if not is_favorited.exists():
            return False
        return True

    def get_is_in_shopping_cart(self, recipe_data):
        user = self.get_user()
        if not user.is_authenticated:
            return False
        is_in_shopping_cart = recipe_data.recipes_shopping_cart.filter(
            user=user, recipe=recipe_data)
        if not is_in_shopping_cart.exists():
            return False
        return True

    def to_representation(self, instance):
        data = super().to_representation(instance)
        ingredients = data.get('ingredients')
        ingredient_amounts = {ir.ingredient.id: ir.amount for
                              ir in instance.recipe_ingredients.all()}
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            ingredient['amount'] = ingredient_amounts.get(ingredient_id)
        return data


class RecipePostPatchSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, write_only=True,
                                              queryset=Tag.objects.all(),
                                              required=True, allow_empty=False)
    author = serializers.HiddenField(default=CurrentUserDefault())
    ingredients = serializers.ListField(required=True, allow_empty=False)

    class Meta(RecipeSerializer.Meta):
        pass

    def validate_tags(self, tags):
        if len(set(tags)) != len(tags):
            raise ValidationError(UNIQUE_TAGS)
        return tags

    def validate_ingredients(self, ingredients):
        ingredients_ids = [ingredient.get('id') for ingredient in ingredients]
        ingredients_amounts = [ingredient.get('amount') for ingredient
                               in ingredients]
        if None in ingredients_ids or None in ingredients_amounts:
            raise ValidationError(NOT_NONE_INGREDIENTS)
        amounts = [int(ingredient.get('amount')) < 1
                   for ingredient in ingredients]
        if any(amounts):
            raise ValidationError(AMOUNT_ABOVE_ONE)
        if len(set(ingredients_ids)) != len(ingredients):
            raise ValidationError(UNIQUE_INGREDIENTS)
        return ingredients

    def create_or_update_ingredients_tags(
            self, recipe, tags=None, ingredients=None):
        recipe.tags.set(tags)

        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount', None)
            if amount is None or int(amount) < 1:
                raise ValidationError(AMOUNT_ABOVE_ONE)
            recipe_ingredient, _ = recipe.recipe_ingredients.get_or_create(
                ingredient_id=ingredient_id)
            recipe_ingredient.amount = amount
            recipe_ingredient.save()
        return recipe

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        return self.create_or_update_ingredients_tags(recipe, tags, ingredients)

    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.save()
        return self.create_or_update_ingredients_tags(
            instance, tags=tags, ingredients=ingredients)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_request(self):
        return self.context.get('request')

    def get_user(self):
        return self.get_request().user

    def get_recipe(self):
        return self.get_request().parser_context.get('kwargs').get('pk')

    def validate(self, shopping_cart_data):
        recipe = get_object_or_404(Recipe, pk=self.get_recipe())
        request = self.get_request()
        user = self.get_user()
        path = request.path
        if recipe.author == user:
            raise ValidationError(USERS_RECIPE)
        if 'shopping_cart' in path:
            if request.method == 'POST':
                if recipe.recipes_shopping_cart.filter(
                        recipe=recipe, user=user,
                        is_in_shopping_cart=True):
                    raise ValidationError(ALREADY_IN_SHOPPING_CART)

            elif request.method == 'DELETE':
                if not recipe.recipes_shopping_cart.filter(
                        recipe=recipe, user=user,
                        is_in_shopping_cart=True):
                    raise ValidationError(NOT_IN_SHOPPING_CART)
        else:
            if request.method == 'POST':
                if recipe.recipes_shopping_cart.filter(
                        recipe=recipe, user=user,
                        is_favorited=True):
                    raise ValidationError(ALREADY_IN_FAVORITED)

            elif request.method == 'DELETE':
                if not recipe.recipes_shopping_cart.filter(
                        recipe=recipe, user=user,
                        is_favorited=True):
                    raise ValidationError(NOT_IN_FAVORED)
        return shopping_cart_data

    def to_representation(self, instance):
        pk = self.get_recipe()
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'id': recipe.id,
            'name': recipe.name,
            'image': self.get_request().build_absolute_uri(recipe.image.url),
            'cooking_time': recipe.cooking_time
        }
        return data
