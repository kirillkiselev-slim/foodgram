from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import GetRecipeByLinkViewSet


app_name = 'recipes'

router = DefaultRouter()
router.register(r'', GetRecipeByLinkViewSet, basename='recipe-uuid')

urlpatterns = [
    path('', include(router.urls)),
]
