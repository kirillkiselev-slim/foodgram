from django.contrib import admin

from .models import CustomUser, Follows


class CustomUserAdmin(admin.ModelAdmin):
    search_fields = (
        'email',
        'username'
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follows)
