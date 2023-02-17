from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Tag, Ingredient, Recipe, IngredientRecipe
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, PostRecipeSerializer,
                          SimpleRecipeSerializer)
from .permissions import IsAuthorOrReadOnlyPermission
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from .pagination import CustomPagination
from .mixins import CreteDestroyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import RecipeFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return PostRecipeSerializer
        return RecipeSerializer


class ShoppingCartViewSet(CreteDestroyModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        current_user = self.request.user
        if current_user.shopping_cart.filter(id=recipe_id):
            data = {"errors": "Рецепт уже есть в списке покупок"}
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=data)
        current_user.shopping_cart.add(recipe)
        dict_obj = model_to_dict(recipe)
        serializer = SimpleRecipeSerializer(recipe, data=dict_obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        current_user = self.request.user
        if current_user.shopping_cart.filter(id=recipe_id):
            current_user.shopping_cart.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {
                "errors": "Данного рецепта нет в списке покупок"
                }
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data=data)


class FavoriteViewSet(CreteDestroyModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        current_user = self.request.user
        if current_user.favorite.filter(id=recipe_id):
            data = {"errors": "Рецепт уже есть в избранном"}
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=data)
        current_user.favorite.add(recipe)
        dict_obj = model_to_dict(recipe)
        serializer = SimpleRecipeSerializer(recipe, data=dict_obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        current_user = self.request.user
        if current_user.favorite.filter(id=recipe_id):
            current_user.favorite.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {
                "errors": "Данного рецепта нет в избранном"
                }
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data=data)


class ShoppindCartPDFView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        current_user = request.user
        shopping_list = current_user.shopping_cart.all()
        shopping_list_dict = dict()
        for recipe in shopping_list:
            ingredients = recipe.ingredients.all()
            for ingredient in ingredients:
                ingredient_name = ingredient.name
                ingredient_amount = get_object_or_404(IngredientRecipe,
                                                      ingredient=ingredient,
                                                      recipe=recipe).amount
                if ingredient_name in shopping_list_dict:
                    shopping_list_dict[ingredient_name] += ingredient_amount
                else:
                    shopping_list_dict[ingredient_name] = ingredient_amount
        string_text = []
        for ingredient, amount in shopping_list_dict.items():
            measurement_unit = get_object_or_404(Ingredient,
                                                 name=ingredient
                                                 ).measurement_unit
            string = f'{ingredient} ({measurement_unit}) - {amount}'
            string_text.append(string)
        text = p.beginText()
        text.setTextOrigin(100, 750)
        for string in string_text:
            text.textLine(text=string)
        p.drawText(text)
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer,
                            as_attachment=True,
                            filename='shopping_cart.pdf')
