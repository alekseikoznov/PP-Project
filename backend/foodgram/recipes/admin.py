from django.contrib import admin

from .models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe


class RecipeAdmin(admin.ModelAdmin):
    def favorite_count(self, obj):
        return obj.user_favorite.all().count()

    favorite_count.short_description = "Количество в избранном"

    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('favorite_count', )


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(TagRecipe)
admin.site.register(Recipe, RecipeAdmin)
