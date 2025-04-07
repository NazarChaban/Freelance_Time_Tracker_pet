from rest_framework import serializers
from clients.models import Client


class ClientReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'website', 'rate',
            'is_active', 'created_at'
        ]
        read_only_fields = fields


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone', 'website', 'rate',
            'is_active', 'created_at'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'website', 'rate', 'is_active']
