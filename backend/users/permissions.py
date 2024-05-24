from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny


class ReadOrAdminOnly(AllowAny):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff


class AuthorOrAdminOnly(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        print(obj.email == request.user)
        return obj.email == request.user or obj.is_staff
