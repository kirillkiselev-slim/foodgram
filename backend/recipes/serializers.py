from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from recipes.models import (Ingredients, Tags, Recipes,
                            TagsRecipes, IngredientsRecipes)
from api.serializers import Base64ImageField
from users.serializers import ProfileSerializer

User = get_user_model()


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class RecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    author = ProfileSerializer(read_only=True)
    tags = TagsSerializer(many=True, required=True)
    ingredients = IngredientsSerializer(many=True, required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def to_internal_value(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredients')
        data['tags'] = [{'id': tag} for tag in tags]
        data[''] = ...
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        print(tags)
        # recipe = Recipes.objects.create(**validated_data)
        #
        # for tag in tags:
        #     current_tag = get_object_or_404(Tags, pk=tag)
        #     TagsRecipes(tag=current_tag, recipe=recipe)


    def get_is_favorited(self, obj):
        ...

    def get_is_in_shopping_cart(self, obj):
        ...

