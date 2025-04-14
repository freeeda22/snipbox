# accounts/serializers.py

from rest_framework import serializers
from .models import User

class UserCreateSerializer(serializers.ModelSerializer):
    """user create serializer"""
    class Meta:
        model = User
        exclude = ["username"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """user update serializer"""
    class Meta:
        model = User
        fields = "__all__"
