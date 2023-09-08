from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField('Название',
                            max_length=200,
                            unique=True,
                            validators=[RegexValidator(
                                regex='^[A-Za-z]+$'
                            )])
    color = models.CharField('Цвет в HEX',
                             max_length=7,
                             default='null',
                             unique=True,
                             validators=[RegexValidator(
                                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
                             )])
    slug = models.SlugField('Уникальный слаг',
                            max_length=200,
                            unique=True,
                            default='null',
                            validators=[RegexValidator(
                                regex='^[-a-zA-Z0-9_]+$'
                             )])

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField('Название',
                            max_length=200,
                            unique=True)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=200)

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
    is_favorited = models.BooleanField('Избранное',
                                       default=False)
    is_in_shopping_cart = models.BooleanField('Корзина',
                                              default=False)
    name = models.CharField('Название блюда',
                            max_length=200)
    image = models.ImageField('Фото блюда',
                              blank=True)
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (мин)',
        validators=[MinValueValidator(limit_value=1,
                                      message='Время должно быть больше 0!')])

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
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(limit_value=1,
                                      message='Введите значение больше 0!')])

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
    """Список покупок пользователя."""

    user = models.ForeignKey(User,
                             related_name='shopping_cart',
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
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
