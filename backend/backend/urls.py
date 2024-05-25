from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),

    # path(r'^api/(auth/[\w/]+(?:in|out)/$|users/([^sub][a-z]+/)?$)',
    #      include('djoser.urls')),
    # path('api/', include('djoser.urls')),

    # path(r'^api/users/\d+|me|[sub]+/(\w+/$)?',
    #      include('users.urls', namespace='users'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
