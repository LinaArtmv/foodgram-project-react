import base64

from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers, status
from users.models import Subscription, User


class Base64ImageField(serializers.ImageField):
    """Кодирует картинку в Base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSignUpSerializer(UserCreateSerializer):
    """Связан с эндпоинтом api/users/ POST."""

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password', 'id')


class UserSerializer(UserSerializer):
    """Сериализует данные для эндпоинтов:
    api/users/ GET
    api/users/{id}/ GET
    api/users/me/ GET."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and obj.following.filter(user=request.user,
                                         author=obj).exists())

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class TagSerialiser(serializers.ModelSerializer):
    """Сериализатор для работы с моделью Tag для эндпоинтов:
    api/tags/ GET, api/tags/{id}/ GET."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с моделью Ingredient для эндпоинтов:
    api/ingredients/ GET, api/ingredients/{id}/ GET."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    amount = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    tags = TagSerialiser(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientReadSerializer(read_only=True, many=True,
                                           source='ingredient_recipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and obj.favorites.filter(user=user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (not user.is_anonymous
                and obj.shopping_cart.filter(user=user, recipe=obj).exists())

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'image', 'name', 'text', 'cooking_time')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецепта."""

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredientWriteSerializer(many=True)
    image = Base64ImageField()

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                {'ingredients': 'Выбери хотя бы один тег!'})
        tag_list = []
        for tag in value:
            if tag in tag_list:
                raise serializers.ValidationError(
                    {'tags': 'Теги не должны повторяться!'})
            tag_list.append(tag)
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Нужно выбрать ингредиент!'})
        ingredients_list = []
        for dict in ingredients:
            ingredient = get_object_or_404(Ingredient, name=dict['id'])
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингридиенты повторяются!'})
            if dict['amount'] <= 0:
                raise serializers.ValidationError(
                    {'amount': 'Количество должно быть больше 0!'})
            if not ('id' and 'amount'):
                raise KeyError('Отсутствует обязательное поле')
            ingredients_list.append(ingredient)
        return value

    def validate(self, data):
        tags = data['tags']
        ingredients = data['ingredients']
        name = data['name']
        text = data['text']
        if not (tags or ingredients):
            raise serializers.ValidationError(
                'Выберите хотя бы одно значение!')
        if Recipe.objects.filter(name=name,
                                 text=text).exists():
            raise serializers.ValidationError(
                'Такой рецепт уже есть!')
        return data

    def _create_ingredient(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients])
        return

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_ingredient(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self._create_ingredient(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeReadSerializer(instance,
                                    context={'request': request}).data

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'image',
                  'name', 'text', 'cooking_time')


class SubscritionRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения подписок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор модели Subscription, методы POST и DELETE."""

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscription.objects.filter(user=user,
                                           author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.author.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = SubscritionRecipeSerializer(recipes,
                                                 many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()

    def validate(self, data):
        user = self.context.get('request').user
        author = self.context.get('author')
        if user.follower.filter(author=author).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны на этого автора!',
                code=status.HTTP_400_BAD_REQUEST,)
        if user == author:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST,)
        return data

    class Meta:
        model = Subscription
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'recipes', 'is_subscribed', 'recipes_count')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Список авторов на которых подписан пользователь."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscription.objects.filter(user=user,
                                           author=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = SubscritionRecipeSerializer(recipes,
                                                 many=True)
        return serializer.data

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор модели ShoppingCart."""

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscritionRecipeSerializer(instance.recipe,
                                           context={'request': request}).data

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        if user.shopping_cart.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Favorite."""

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscritionRecipeSerializer(instance.recipe,
                                           context={'request': request}).data

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        if user.favorites.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное')
        return data

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')
