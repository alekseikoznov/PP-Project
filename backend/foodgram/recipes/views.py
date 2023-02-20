import io

from django.forms.models import model_to_dict
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .mixins import CreteDestroyModelViewSet
from .models import Ingredient, Recipe, Tag
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (IngredientSerializer, PostRecipeSerializer,
                          RecipeSerializer, SimpleRecipeSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
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
        dict_obj = model_to_dict(recipe)
        serializer = SimpleRecipeSerializer(
            recipe,
            data=dict_obj,
            context={'request': self.request,
                     'recipe': recipe,
                     'class': 'shopping_cart'})
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
        dict_obj = model_to_dict(recipe)
        serializer = SimpleRecipeSerializer(
            recipe,
            data=dict_obj,
            context={'request': self.request,
                     'recipe': recipe,
                     'class': 'shopping_cart'})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        current_user = self.request.user
        current_user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(CreteDestroyModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        dict_obj = model_to_dict(recipe)
        serializer = SimpleRecipeSerializer(
            recipe,
            data=dict_obj,
            context={'request': self.request,
                     'recipe': recipe,
                     'class': 'favorite'})
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
        dict_obj = model_to_dict(recipe)
        serializer = SimpleRecipeSerializer(
            recipe,
            data=dict_obj,
            context={'request': self.request,
                     'recipe': recipe,
                     'class': 'favorite'})
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        current_user.favorite.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppindCartPDFView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        buffer = io.BytesIO()
        pdfmetrics.registerFont(TTFont('TenorSans', './fonts/TenorSans.ttf'))
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont('TenorSans', 16)
        string_text = request.user.get_text()
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
