from rest_framework import mixins, viewsets


class CreteDestroyModelViewSet(mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class ListModelViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    pass
