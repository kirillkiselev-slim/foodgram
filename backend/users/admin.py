from django.contrib import admin
from .models import CustomUser, Follows



admin.site.register(CustomUser)
admin.site.register(Follows)
