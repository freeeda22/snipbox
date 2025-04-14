from django.conf import settings
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from .models import Snippet, Tag
from .serializers import ( 
    SnippetCreateSerializer,
    SnippetDetailSerializer,
    SnippetOverviewSerializer,
    TagSerializer,
)
from django.db import transaction
from rest_framework.generics import ( 
    CreateAPIView,
    RetrieveAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
    DestroyAPIView
)
from rest_framework.exceptions import PermissionDenied, NotFound
from django.contrib.auth import get_user_model

User = get_user_model()  

class SnippetCreateAPI(CreateAPIView):
    """ snippet create api"""
    serializer_class = SnippetCreateSerializer

    def create(self, request, *args, **kwargs):
        data = request.data  #getting input
        tag_title = data.pop("tag", None) #getting tag data from input data

        with transaction.atomic(): #begin transaction
            if tag_title:
                tag = Tag.objects.filter(title=tag_title).first()
                if not tag:
                    tag = Tag(title=tag_title, created_by=self.request.user)
                    tag.save()
                data["tag"] = tag.id
            serializer = self.get_serializer(data=data) 
            if serializer.is_valid(): #checking with serializer
                obj= serializer.save(created_by=request.user)#updating created user
                send_mail(
                    subject='New Snippet Created',
                    message = (
                        f'Hi {obj.created_by.first_name},\n\n'
                        f'Your snippet "{obj.title}" was created successfully.\n'
                        f'Thank you for using SnipBox!\n\n'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.created_by.email],
                    fail_silently=False,
                )
                data = {
                    "message" : "Snippet Created Successfully",
                    "data" : serializer.data
                }
                return Response(data, status=status.HTTP_201_CREATED)  #success response
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) #error response

class SnippetDetailAPIView(RetrieveAPIView):
    """snippet detail api"""
    serializer_class = SnippetDetailSerializer

    def get_object(self):
        """
        This view should return the snippet for the current user.
        """
        pk = self.kwargs.get('pk')
        try:
            obj = Snippet.objects.select_related('created_by','tag').only(  #filtering data
                'id', 
                'record_id',
                'title', 
                'note', 
                'created_at',
                'updated_at',
                'created_by__username',
                'tag__id',
                'tag__title',
            ).get(pk=pk)
            if obj.created_by != self.request.user:
                raise PermissionDenied("You do not have permission to access this snippet.")
            return obj
        except Snippet.DoesNotExist:
            raise NotFound("Snippet not found.")

class SnippetOverviewAPI(ListAPIView):
    """ snippet overview api"""
    serializer_class = SnippetOverviewSerializer

    def get_queryset(self):
        snippet_obj = Snippet.objects.filter(created_by=self.request.user).select_related(
            'created_by','tag').only(  #filtering data
            'id', 
            'record_id',
            'title', 
            'note', 
            'created_at',
            'updated_at',
            'created_by__username',
            'tag__id',
            'tag__title') #filtering according to created user
        return snippet_obj

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset() #getting queryset 
        serializer = self.get_serializer(queryset, many=True, context={'request': request}) #serializing data
        return Response({
            "total_snippets": queryset.count(), #getting total count
            "snippets": serializer.data #serialized data
        })

class SnippetUpdateAPI(RetrieveUpdateAPIView):
    """snippet update api"""
    serializer_class = SnippetDetailSerializer
    queryset = Snippet.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  #fetches the Snippet instance based on the URL 
        if instance.created_by != self.request.user:
            return Response({"detail": "You do not have permission to edit this snippet."}, status=403)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True) #Validates the data
        self.perform_update(serializer) #updating data 
        send_mail(
            subject='Snippet Updated',
            message = (
                f'Hi {instance.created_by.first_name},\n\n'
                f'Your snippet "{instance.record_id}" was updated successfully.\n'
                f'Thank you for using SnipBox!\n\n'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.created_by.email],
            fail_silently=False,
        ) 
        return Response(serializer.data)  # Return updated data

class SnippetDeleteAPI(DestroyAPIView):
    """snippet delete api"""
    serializer_class = SnippetDetailSerializer
    queryset = Snippet.objects.all()

    def delete(self, request, *args, **kwargs):
        snippet_ids = request.data.get('snippet_ids', []) #getting data as an array for multiple delete
        if not snippet_ids: #checking whether data in the input payload
            return Response({"detail": "No snippet IDs provided."}, status=400)
        snippets = Snippet.objects.filter(id__in=snippet_ids) #filtering according to the input data
        snippets.delete() #deleting the filtered data
        remaining_snippets = Snippet.objects.filter(created_by=request.user) #filtering other exists data of created user
        serializer = SnippetDetailSerializer(remaining_snippets, many=True) #serializing the data
        deleted_count = len(snippet_ids)
        message = (
            f'Hi {self.request.user.first_name},\n\n'
            f'{deleted_count} snippet(s) have been deleted from your SnipBox account.\n'
            f'Thank you for staying organized with SnipBox!\n\n'
        )
        send_mail(
            subject='Snippets Deleted',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.request.user.email],
            fail_silently=False,
        )
        return Response({
            "total_snippets": remaining_snippets.count(), #getting count
            "snippets": serializer.data #returning the filtered data as a response
        })

class TagListAPI(ListAPIView):
    """tag serilalizer"""
    serializer_class = TagSerializer

    def list(self, request, *args, **kwargs):
        tags = ( Tag.objects.all().select_related('created_by'
                                                  ).only('id','tag_id','title','created_by__username'))
        serializer = TagSerializer(tags, many=True)
        
        # Return the response with the total count and list of tags
        return Response({
            "total_tags": tags.count(),
            "tags": serializer.data
        })

class SnippetsByTagAPI(ListAPIView):
    """ snippet list according to tag"""
    serializer_class = SnippetDetailSerializer

    def list(self, request, *args, **kwargs):
        tag_id = kwargs.get('tag_id')  #getting tag id
        snippets = Snippet.objects.filter(tag__id=tag_id).select_related('created_by','tag').only( #filtering data
            'id', 
            'record_id',
            'title', 
            'note', 
            'created_at',
            'updated_at',
            'created_by__username',
            'tag__id',
            'tag__title',
        )

        serializer = SnippetDetailSerializer(snippets, many=True)
        return Response({
            "total_snippets": snippets.count(), #getting count
            "snippets": serializer.data # return response
        })
