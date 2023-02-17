from rest_framework import routers

from django.urls import include, path
from .views import CreateDeleteSubViewSet, SubscriptionsViewSet

router = routers.DefaultRouter()
router.register(r'users/(?P<user_id>\d+)/subscribe', CreateDeleteSubViewSet,
                basename='subscribe',)
router.register('users/subscriptions', SubscriptionsViewSet,
                basename='subscriptions',)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
