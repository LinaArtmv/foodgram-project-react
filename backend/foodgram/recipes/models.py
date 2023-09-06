from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(max_length=200,
                            verbose_name='Название',
                            unique=True)
    color = models.CharField(max_length=7,
                             verbose_name='Цвет в HEX',
                             default='null',
                             unique=True)
    slug = models.SlugField(max_length=200,
                            unique=True,
                            default='null',
                            verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=200,
                            verbose_name='Название',
                            unique=True)
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги',
                                  through='TagRecipe')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Ингредиенты',
                                         through='IngredientRecipe')
    is_favorited = models.BooleanField(default=False,
                                       verbose_name='Избранное')
    is_in_shopping_cart = models.BooleanField(default=False,
                                              verbose_name='Корзина')
    name = models.CharField(max_length=200,
                            verbose_name='Название блюда')
    image = models.ImageField(verbose_name='Фото блюда',
                              upload_to='recipes/',
                              blank=True)
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин)')

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """Связующая модель для рецептов и тегов."""

    recipe = models.ForeignKey(Recipe,
                               related_name='tag_recipe',
                               on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag,
                            related_name='tag_recipe',
                            on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class IngredientRecipe(models.Model):
    """Связующая модель для ингредиентов и рецептов."""

    recipe = models.ForeignKey(Recipe,
                               related_name='ingredient_recipe',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   related_name='ingredient_recipe',
                                   on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'Количество'
        verbose_name_plural = 'Количество'

    def __str__(self):
        return (f'{self.recipe.name} содержит '
                f'{self.amount} {self.ingredient.name}')


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    user = models.ForeignKey(User,
                             related_name='favorites',
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               related_name='favorites',
                               on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user.username} понравился {self.recipe.name}'


class ShoppingCart(models.Model):
    """
    Список покупок пользователя.
    Ограничения уникальности полей:
      author, recipe.
    """
    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Рецепт для приготовления',
        on_delete=models.CASCADE,
        help_text='Выберите рецепт для приготовления')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_cart')]

    def __str__(self):
        return f'{self.recipe}'
