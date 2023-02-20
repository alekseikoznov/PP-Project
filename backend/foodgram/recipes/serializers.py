import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from .models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

    def serialize_ingredientrecipe(self, ingredient_instance):
        if self.context.get("recipe_instance"):
            ingredientrecipe_instance = (
                ingredient_instance.ingredientrecipes.filter(
                    recipe=self.context["recipe_instance"]).first())
            return IngredientRecipeSerializer(ingredientrecipe_instance).data
        return False

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if self.serialize_ingredientrecipe(instance):
            return {**rep, **self.serialize_ingredientrecipe(instance)}
        return rep


class IngredientRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientRecipe
        fields = ('amount',)


class RecipeSerializer(serializers.ModelSerializer):
    """GET запрос рецепта"""

    tags = TagSerializer(many=True, required=True)
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_ingredients(self, recipe):
        return IngredientSerializer(
            recipe.ingredients.all(),
            many=True,
            context={"recipe_instance": recipe}
        ).data

    def get_is_favorited(self, recipe):
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.favorite.filter(id=recipe.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        current_user = self.context.get('request').user
        if not current_user.is_authenticated:
            return False
        return current_user.shopping_cart.filter(id=recipe.id).exists()


class PostRecipeSerializer(serializers.ModelSerializer):
    """POST и PATCH запрос на создание рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=True,
        many=True
    )
    ingredients = serializers.ListField()
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def create(self, validated_data):
        validated_data['author'] = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        ingredients_list = []
        tags_list = []
        for ingredient in ingredients:
            id = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_unit = Ingredient.objects.get(id=id)
            ingredients_list.append(
                IngredientRecipe(ingredient=ingredient_unit,
                                 recipe=recipe,
                                 amount=amount))
        IngredientRecipe.objects.bulk_create(ingredients_list)
        for tag in tags:
            tags_list.append(TagRecipe(tag=tag, recipe=recipe))
        TagRecipe.objects.bulk_create(tags_list)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name')
        instance.image = validated_data.get('image')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.ingredients.clear()
        for ingredient in ingredients:
            id = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_unit = Ingredient.objects.get(id=id)
            IngredientRecipe.objects.get_or_create(ingredient=ingredient_unit,
                                                   recipe=instance,
                                                   amount=amount)
        instance.tags.clear()
        for tag in tags:
            TagRecipe.objects.get_or_create(tag=tag, recipe=instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class SimpleRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        method_class = self.context.get('class')
        current_user = self.context.get('request').user
        recipe = self.context.get('recipe')
        if self.context.get('request').method == 'DELETE':
            if method_class == 'favorite':
                if not current_user.favorite.filter(id=recipe.id):
                    raise serializers.ValidationError({
                        "errors": "Данного рецепта нет в избранном"
                        })
            elif method_class == 'shopping_cart':
                if not current_user.shopping_cart.filter(id=recipe.id):
                    raise serializers.ValidationError({
                        "errors": "Данного рецепта нет в списке покупок"
                        })
            return data
        if method_class == 'favorite':
            if current_user.favorite.filter(id=recipe.id):
                raise serializers.ValidationError({
                    "errors": "Рецепт уже есть в избранном"
                    })
            current_user.favorite.add(recipe)
        elif method_class == 'shopping_cart':
            if current_user.shopping_cart.filter(id=recipe.id):
                raise serializers.ValidationError({
                    "errors": "Рецепт уже есть в списке покупок"
                    })
            current_user.shopping_cart.add(recipe)
        return data
