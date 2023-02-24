import recipes.models as rcp
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import get_object_or_404


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    subscriptions = models.ManyToManyField(
        "self", blank=True, related_name="followers", symmetrical=False
    )
    favorite = models.ManyToManyField('recipes.recipe',
                                      related_name="user_favorite", blank=True)
    shopping_cart = models.ManyToManyField('recipes.recipe',
                                           related_name="user_shopping_cart",
                                           blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        indexes = [
            models.Index(fields=['email', ]),
            models.Index(fields=['username', ]),
            ]

    def get_text(self):
        shopping_list = self.shopping_cart.all()
        shopping_list_dict = dict()
        string_text = []
        for recipe in shopping_list:
            ingredients = recipe.ingredients.all()
            for ingredient in ingredients:
                ingredient_name = ingredient.name
                ingredient_amount = get_object_or_404(rcp.IngredientRecipe,
                                                      ingredient=ingredient,
                                                      recipe=recipe).amount
                measurement_unit = get_object_or_404(rcp.Ingredient,
                                                     name=ingredient_name
                                                     ).measurement_unit
                if ingredient_name in shopping_list_dict:
                    shopping_list_dict[ingredient_name][0] += ingredient_amount
                else:
                    shopping_list_dict[ingredient_name] = [ingredient_amount,
                                                           measurement_unit]
        for ingredient, amount_unit in shopping_list_dict.items():
            string = f'{ingredient} ({amount_unit[1]}) - {amount_unit[0]}'
            string_text.append(string)
        return string_text

    def __str__(self):
        return self.username
