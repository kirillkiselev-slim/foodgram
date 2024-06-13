from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (UserFoodgramViewSet, IngredientViewSet,
                       TagsViewSet, RecipesViewSet)


app_name = 'api'


router = DefaultRouter()
router.register(r'users', UserFoodgramViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
