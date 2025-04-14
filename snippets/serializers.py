from rest_framework import serializers
from .models import Snippet,Tag

class SnippetCreateSerializer(serializers.ModelSerializer):
    """ snippet create serializer"""
    class Meta:
        model = Snippet
        exclude = ["created_by"]

class SnippetDetailSerializer(serializers.ModelSerializer):
    """ snippet detail serializer"""
    created_by = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    updated_date = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()

    def get_created_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else None
    
    def get_updated_date(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d') if obj.updated_at else None

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None
    
    def get_tag(self, obj):
        tag = getattr(obj, 'tag', None)
        if tag:
            return {
                "id": tag.id,
                "title": tag.title
            }
        return None
    
    
    class Meta:
        model = Snippet
        fields = [ 
            'id', 
            'record_id',
            'title', 
            'note', 
            'created_date',
            'updated_date',
            'created_by',
            'tag'
            ] 

class SnippetOverviewSerializer(serializers.ModelSerializer):
    """ snippet overview serializer"""
    url = serializers.HyperlinkedIdentityField(
        view_name='snippet-detail',  # Make sure this matches your URL name
        lookup_field='pk',
        read_only=True
    )
    created_date = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()

    def get_created_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else None
    
    def get_tag(self, obj):
        tag = getattr(obj, 'tag', None)
        if tag:
            return {
                "id": tag.id,
                "title": tag.title
            }
        return None
    
    
    class Meta:
        model = Snippet
        fields = [ 
            'id', 
            'record_id',
            'title', 
            'note', 
            'created_date',
            'tag',
            'url',
            ] 
