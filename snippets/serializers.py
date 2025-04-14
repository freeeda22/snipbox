from rest_framework import serializers
from .models import Snippet,Tag

class SnippetCreateSerializer(serializers.ModelSerializer):
    """ snippet create serializer"""
    class Meta:
        model = Snippet
        exclude = ["created_by"]