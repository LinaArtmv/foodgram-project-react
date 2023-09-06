from django.contrib import admin
from .models import (Favorite, Ingredient, IngredientRecipe,
                     TagRecipe, Recipe, ShoppingCart, Tag)


class IngredientsInline(admin.TabularInline):
    """
    Админ-зона для интеграции добавления ингридиентов в рецепты.
    Сразу доступно добавление 3х ингрдиентов.
    """
    model = IngredientRecipe
    extra = 3


class TagsInline(admin.TabularInline):
    """
    Админ-зона для интеграции добавления ингридиентов в рецепты.
    Сразу доступно добавление 3х ингрдиентов.
    """
    model = TagRecipe
    extra = 3


class FavoriteAdmin(admin.ModelAdmin):
    """
    Админ-зона избранных рецептов.
    """
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Админ-зона покупок.
    """
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


class IngredientRecipeAdmin(admin.ModelAdmin):
    """
    Админ-зона ингридентов для рецептов.
    """
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-зона рецептов.
    Добавлен просмотр кол-ва добавленных рецептов в избранное.
    """
    list_display = ('id', 'author', 'name')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('ingredients',)
    filter_vertical = ('tags',)
    empty_value_display = '-пусто-'
    inlines = [IngredientsInline, TagsInline]

    def in_favorite(self, obj):
        return obj.favorite.all().count()

    in_favorite.short_description = 'Добавленные рецепты в избранное'


class TagAdmin(admin.ModelAdmin):
    """
    Админ-зона тегов.
    """
    list_display = ('id', 'name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-зона ингридиентов.
    """
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
