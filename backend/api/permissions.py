from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny


class ReadOrAdminOnly(AllowAny):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff


class AuthorOrAdminOnly(IsAuthenticated):

    def has_object_permission(self, request, view, user_data):
        return user_data.email == request.user or request.user.is_staff


class RecipeAuthorOrAdminOnly(IsAuthenticated):

    def has_object_permission(self, request, view, user_data):
        return user_data.author == request.user or request.user.is_staff
