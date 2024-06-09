from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet
from recipes.views import IngredientViewSet, TagsViewSet, RecipesViewSet


app_name = 'api'


router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
