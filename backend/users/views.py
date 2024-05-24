from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions

from djoser.views import UserViewSet
from users.permissions import AuthorOrAdminOnly, ReadOrAdminOnly
from users.serializers import FollowSerializer
from users.models import Follows
from django.db.models import Subquery


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = (ReadOrAdminOnly,)
        elif self.action == 'avatar':
            self.permission_classes = (AuthorOrAdminOnly,)
        elif self.action in ('subscribe', 'subscriptions'):
            self.permission_classes = (AuthorOrAdminOnly,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('subscribe', 'subscriptions'):
            return FollowSerializer
        return super().get_serializer_class()

    @action(['patch', 'delete'], detail=True)
    def avatar(self, request, *args, **kwargs):
        user = self.request.user
        if request.method == 'PATCH':
            serializer = self.get_serializer(user,
                                             data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'avatar': serializer.data.get('avatar')},
                            status=status.HTTP_200_OK)
        user.avatar = 'default.png'
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        user = self.request.user.id
        follower = self.request.parser_context.get('kwargs').get('id')
        if request.method == 'POST':
            serializer = self.get_serializer(user,
                                             data=request.data)
            serializer.is_valid(raise_exception=True)
            user_instance = get_object_or_404(User, pk=user)
            follower_instance = get_object_or_404(User, pk=follower)
            Follows.objects.create(user=user_instance,
                                   following=follower_instance)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Follows.objects.filter(user=user, following=follower).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.request.user.id)
        following_ids = Follows.objects.filter(user_id=user.id).values('following_id')
        queryset = User.objects.filter(id__in=Subquery(following_ids))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
