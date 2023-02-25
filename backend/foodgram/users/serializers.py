import recipes.serializers as rcp
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.followers.filter(id=user.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class SubscriptionsSerializer(CustomUserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes_count', 'recipes')

    def validate(self, data):
        current_user = self.context.get('request').user
        author = self.context.get('author')
        if self.context.get('request').method == 'DELETE':
            if not current_user.subscriptions.filter(id=author.id):
                raise serializers.ValidationError({
                    "errors": "Вы не были подписаны"
                    })
            return data
        if current_user == author:
            raise serializers.ValidationError({
                "errors": "Нельзя подписаться на себя!"
                })
        if current_user.subscriptions.filter(id=author.id):
            raise serializers.ValidationError({
                "errors": "Вы уже подписаны!"
                })
        current_user.subscriptions.add(author)
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        recipes_limit = int(self.context.get('request').GET.get('recipes_limit'))
        recipes = obj.recipes.all()[:recipes_limit]
        serializer_class = rcp.SimpleRecipeSerializer
        serializer = serializer_class(
            many=True,
            instance=recipes
        )
        return serializer.data
