import base64

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from django.core.files.base import ContentFile

from users.models import Follows, CustomUser
from users.constants import CANNOT_FOLLOW_YOURSELF, ALREADY_FOLLOWS

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request.headers.get('Authorization'):
            return False

        if request.method == 'POST' and request.path != '/api/users/':  # When user subscribes via POST request.
            return True

        user = get_object_or_404(User, pk=request.user.id)
        follower = get_object_or_404(User, pk=obj.id)
        return user.follows.filter(following=follower).exists()


class FollowSerializer(ProfileSerializer):
    # TODO - add many to many recipes filed
    # TODO - add serializer method field to count these recipes

    class Meta(ProfileSerializer.Meta):
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'avatar')

    def validate(self, follower_data):
        request = self.context.get('request')
        follower = int(self.context.get('view').kwargs.get('id'))
        user = request.user.id
        if user == follower:
            raise serializers.ValidationError(CANNOT_FOLLOW_YOURSELF)
        elif Follows.objects.filter(user=user, following=follower):
            raise serializers.ValidationError(ALREADY_FOLLOWS)
        return follower_data

    def to_representation(self, instance):
        request = self.context.get('request')
        if request.method == 'GET':
            return ProfileSerializer(instance, context=self.context).data
        user = get_object_or_404(User, pk=instance)
        return ProfileSerializer(user, context=self.context).data
