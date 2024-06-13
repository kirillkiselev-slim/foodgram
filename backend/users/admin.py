from django.contrib import admin

from .models import User, Follows


class UserAdmin(admin.ModelAdmin):
    search_fields = (
        'email',
        'username'
    )


admin.site.register(User, UserAdmin)
admin.site.register(Follows)
