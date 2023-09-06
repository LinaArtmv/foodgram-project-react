from rest_framework import viewsets
from recipes.models import (Tag, Ingredient, Recipe, Favorite,
                            ShoppingCart, IngredientRecipe)
from users.models import User, Subscription
from .serializers import (TagSerialiser, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          SubscriptionSerializer, ShoppingCartSerializer,
                          FavoriteSerializer)
from rest_framework import permissions
from .permissions import IsOwnerOrAdminOrReadOnly
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.shortcuts import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter, RecipeFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет обработки эндпоинтов
    api/tags/ GET, api/tags/{id}/ GET."""

    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет обработки эндпоинтов
    api/ingredients/ GET, api/ingredients/{id}/ GET."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет обработки эндпоинтов
    api/recipes/ GET, POST,
    api/recipes/{id}/ GET, PATCH, DELETE,
    api/recipes/download_shopping_cart/ GET,
    api/recipes/{id}/shopping_cart/ POST, DELETE,
    api/recipes/{id}/favorite/ POST, DELETE."""

    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=self.request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        user = self.request.user
        recipe = Recipe.objects.get(id=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
                raise ValueError('Вы уже добавили рецепт!')
            serializer = ShoppingCartSerializer(data=request.data,
                                                context={'request': request,
                                                         'recipe': recipe})
            if serializer.is_valid(raise_exception=True):
                serializer.save(recipe=recipe, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
                ShoppingCart.objects.get(recipe=recipe).delete()
                return Response('Успешное удаление!',
                                status=status.HTTP_204_NO_CONTENT)
            raise ValueError('Вы ещё не добавили рецепт!')
        return Response({'errors': 'Объект не найден'},
                        status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        user = self.request.user
        recipe = Recipe.objects.get(id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(recipe=recipe, user=user).exists():
                raise ValueError('Вы уже добавили рецепт!')
            serializer = FavoriteSerializer(data=request.data,
                                            context={'request': request,
                                                     'recipe': recipe})
            if serializer.is_valid(raise_exception=True):
                serializer.save(recipe=recipe, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if request.method == 'DELETE':
            if Favorite.objects.filter(recipe=recipe, user=user).exists():
                Favorite.objects.get(recipe=recipe).delete()
                return Response('Успешное удаление!',
                                status=status.HTTP_204_NO_CONTENT)
            raise ValueError('Вы ещё не добавили рецепт!')
        return Response({'errors': 'Объект не найден'},
                        status=status.HTTP_404_NOT_FOUND)


class CustomUserViewSet(UserViewSet):
    """Необходим для обработки эндпоитов
    api/users/subscriptions/ GET,
    api/users/{id}/subscribe/ POST, DELETE."""

    queryset = User.objects.all()

    @action(methods=['get'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        serializer = SubscriptionSerializer(subscriptions,
                                            many=True,
                                            context={'request': request})
        return Response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id):
        user = self.request.user
        author = User.objects.get(id=id)
        if request.method == 'POST':
            if Subscription.objects.filter(author=author, user=user).exists():
                raise ValueError('Вы уже подписаны на этого автора!')
            serializer = SubscriptionSerializer(data=request.data,
                                                context={'request': request,
                                                         'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if request.method == 'DELETE':
            if Subscription.objects.filter(author=author, user=user).exists():
                Subscription.objects.get(author=author).delete()
                return Response('Успешная отписка!',
                                status=status.HTTP_204_NO_CONTENT)
            raise ValueError('Вы ещё не подписаны на этого автора!')
        return Response({'errors': 'Объект не найден'},
                        status=status.HTTP_404_NOT_FOUND)
