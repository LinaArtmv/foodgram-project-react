from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import (TagViewSet, IngredientViewSet,
                    RecipeViewSet, CustomUserViewSet)


router = SimpleRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls'))
]
