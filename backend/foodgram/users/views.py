from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import SubscriptionsSerializer
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from recipes.pagination import CustomPagination
from recipes.mixins import CreteDestroyModelViewSet, ListModelViewSet
from rest_framework.permissions import IsAuthenticated


class CreateDeleteSubViewSet(CreteDestroyModelViewSet):
    serializer_class = SubscriptionsSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        author_id = self.kwargs['user_id']
        author_to_subscribe = get_object_or_404(CustomUser, id=author_id)
        current_user = self.request.user
        if current_user == author_to_subscribe:
            data = {
                    "errors": "Нельзя подписаться на себя"
                    }
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=data)
        if current_user.subscriptions.filter(id=author_id):
            data = {
                    "errors": "Вы уже подписаны"
                    }
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=data)
        current_user.subscriptions.add(author_to_subscribe)
        dict_obj = model_to_dict(author_to_subscribe)
        serializer = SubscriptionsSerializer(author_to_subscribe,
                                             data=dict_obj,
                                             context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        author_id = self.kwargs['user_id']
        author_to_subscribe = get_object_or_404(CustomUser, id=author_id)
        current_user = self.request.user
        if current_user.subscriptions.filter(id=author_id):
            current_user.subscriptions.remove(author_to_subscribe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {
                "errors": "Вы не были подписаны"
                }
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data=data)


class SubscriptionsViewSet(ListModelViewSet):
    serializer_class = SubscriptionsSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.subscriptions.all()
