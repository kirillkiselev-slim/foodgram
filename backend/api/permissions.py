from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny


class ReadOrAdminOnly(AllowAny):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class AuthorOrAdminOnly(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if not view.__dict__.get('basename') == 'recipes':
            return obj.email == request.user or obj.is_staff
        return obj.author == request.user or request.user.is_staff
