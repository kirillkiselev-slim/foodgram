from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

app_name = 'users'


router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
# router.register(r'auth/', include('djoser.urls.authtoken'), basename='auth'),

# user_patterns = [
#     path('', CustomUserViewSet.as_view()),
    # path('subscriptions/', ),
    # path(r'(?P<int:pk>\d+)?/',),
    # path(r'(?P<int:pk>\d+)?/subscribe/')
# ]
#
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
