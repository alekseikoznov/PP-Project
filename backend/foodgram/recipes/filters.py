import django_filters
from rest_framework.filters import SearchFilter

from .models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name="tags__slug",
        method="get_tags",
    )

    author = django_filters.CharFilter(field_name='author__id',
                                       lookup_expr='exact')
    is_favorited = django_filters.NumberFilter(
        field_name="user_favorite",
        method="get_user_field",
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        field_name="user_shopping_cart",
        method="get_user_field",
    )

    def get_tags(self, queryset, field_name, value):
        return queryset.filter(tags__slug__in=self.request.GET.getlist('tags')).distinct()

    def get_user_field(self, queryset, field_name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        dict_field_user = {f"{field_name}__in": (user,)}
        if value == 0:
            return queryset.exclude(**dict_field_user)
        return queryset.filter(**dict_field_user)

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags'
        )
