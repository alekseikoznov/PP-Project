from django.db import models
from django.contrib.auth.models import AbstractUser


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

    def __str__(self):
        return self.username
