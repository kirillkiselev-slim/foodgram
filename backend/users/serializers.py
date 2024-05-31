from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import Follows, CustomUser
from api.constants import CANNOT_FOLLOW_YOURSELF, ALREADY_FOLLOWS
from recipes.models import Recipe
from api.serializers import Base64ImageField

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.follows.filter(following=obj.id).exists()


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
        user_id = request.user.id
        if user_id == self.follower_id():
            raise serializers.ValidationError(CANNOT_FOLLOW_YOURSELF)
        elif Follows.objects.filter(user=user_id, following=self.follower_id()):
            raise serializers.ValidationError(ALREADY_FOLLOWS)
        return follower_data

    def get_recipes(self, obj):
        return Recipe.objects.filter(author=obj)

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def to_representation(self, instance):
        request = self.context.get('request')
        if request.method == 'POST':
            instance = get_object_or_404(User, pk=self.follower_id())

        data = super().to_representation(instance)
        data['recipes'] = [
            {'id': recipe.id, 'name': recipe.name,
             'image': request.build_absolute_uri(recipe.image.url),
             'cooking_time': recipe.cooking_time}
            for recipe in instance.recipes.all()
        ]
        return data
