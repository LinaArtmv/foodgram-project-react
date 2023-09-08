from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


class IngredientsInline(admin.TabularInline):
    """Админ-зона для добавления ингредиентов в рецепты."""

    model = IngredientRecipe
    extra = 3


class TagsInline(admin.TabularInline):
    """Админ-зона для добавления тегов в рецепты."""

    model = TagRecipe
    extra = 3


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-зона избранных рецептов."""

    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-зона списка покупок."""

    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Админ-зона ингредиентов для рецептов."""

    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-зона рецептов."""

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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-зона тегов."""

    list_display = ('id', 'name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-зона ингридиентов."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
