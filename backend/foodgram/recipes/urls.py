from rest_framework import routers
from django.urls import include, path
from recipes.views import (TagViewSet, IngredientViewSet, RecipeViewSet,
                           ShoppingCartViewSet, FavoriteViewSet,
                           ShoppindCartPDFView)

router = routers.DefaultRouter()
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingCartViewSet, basename='shopping_cart',)
router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet,
                basename='favorite',)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)


urlpatterns = [
    path('recipes/download_shopping_cart/', ShoppindCartPDFView.as_view()),
    path('', include(router.urls)),
]
