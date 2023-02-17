from django.db import models
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    color = models.CharField(unique=True, max_length=7)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, related_name='recipes',
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipe/images/'
        )
    ingredients = models.ManyToManyField(Ingredient, through='Ingredientrecipe'
                                         )
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredientrecipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredientrecipes')
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'
