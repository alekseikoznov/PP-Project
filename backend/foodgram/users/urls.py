from django.urls import include, path
from rest_framework import routers

from .views import (CreateDeleteSubViewSet, CustomUserViewSet,
                    SubscriptionsViewSet)

router = routers.DefaultRouter()

router.register(r'users/(?P<user_id>\d+)/subscribe', CreateDeleteSubViewSet,
                basename='subscribe',)
router.register('users/subscriptions', SubscriptionsViewSet,
                basename='subscriptions',)
router.register('users', CustomUserViewSet, basename='users',)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
