from django.contrib import admin

from recipes.models import Ingredient, Tag, Recipe, ShoppingCart, IngredientRecipe

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(ShoppingCart)
admin.site.register(IngredientRecipe)