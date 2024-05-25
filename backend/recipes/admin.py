from django.contrib import admin

from recipes.models import Ingredients, Tags, Recipes

admin.site.register(Ingredients)
admin.site.register(Tags)
admin.site.register(Recipes)
