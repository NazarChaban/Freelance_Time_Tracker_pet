from clients.api.serializers import (
    ClientReadSerializer, ClientCreateSerializer, ClientUpdateSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from clients.models import Client


class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ClientCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClientUpdateSerializer
        else:
            return ClientReadSerializer

    @action(detail=False, methods=['get'], url_path='active')
    def active(self, request):
        clients = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(clients, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='inactive')
    def inactive(self, request):
        clients = self.get_queryset().filter(is_active=False)
        serializer = self.get_serializer(clients, many=True)
        return Response(serializer.data)
