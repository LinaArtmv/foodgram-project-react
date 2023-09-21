from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          RecipeUpdateSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, SubscriptionsSerializer,
                          TagSerialiser)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для TaSerialiser."""

    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для IngredientSerializer."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для RecipeReadSerializer - чтение,
    RecipeWriteSerializer - запись данных."""

    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        if self.action in ('update', 'partial_update'):
            return RecipeUpdateSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def _post_delete_methods(self, request, model, serializer, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = serializer(
                data=request.data,
                context={'request': request,
                         'recipe': recipe})
            if serializer.is_valid(raise_exception=True):
                serializer.save(recipe=recipe, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if model.objects.filter(recipe=recipe, user=user).exists():
                model.objects.get(recipe=recipe).delete()
                return Response('Успешное удаление!',
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=False,
            methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
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
        shopping_cart = ShoppingCart
        serializer = ShoppingCartSerializer
        return self._post_delete_methods(request,
                                         shopping_cart,
                                         serializer,
                                         pk)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        favorite = Favorite
        serializer = FavoriteSerializer
        return self._post_delete_methods(request, favorite, serializer, pk)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для SubscriptionSerializer."""

    queryset = User.objects.all()

    @action(methods=['get'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(pages,
                                             many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data=request.data,
                context={'request': request,
                         'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if Subscription.objects.filter(author=author, user=user).exists():
                Subscription.objects.get(author=author).delete()
                return Response('Успешная отписка!',
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
