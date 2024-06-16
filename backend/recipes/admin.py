from django.contrib import admin

from recipes.models import (Ingredient, Tag, Recipe,
                            ShoppingCart, IngredientRecipe,
                            Favorite)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    inlines = (IngredientRecipeInline,)
    search_fields = (
        'name',
        'author__email'
    )
    list_filter = ('tags',)
    filter_horizontal = (
        'tags',
        'ingredients'
    )
    readonly_fields = ('is_favorited_count',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
        'is_in_shopping_cart',
    )
    list_editable = (
        'is_in_shopping_cart',
    )


class FavoriteCartAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
        'is_favorited',
    )
    list_editable = (
        'is_favorited',
    )


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe'
    )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteCartAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
