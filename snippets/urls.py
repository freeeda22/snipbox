from django.urls import path
from .views import *

urlpatterns = [
    path('create/', SnippetCreateAPI.as_view()),
    path('detail/<int:pk>/', SnippetDetailAPIView.as_view(), name='snippet-detail'),
    path('overview/list/', SnippetOverviewAPI.as_view()),
    path('edit/<int:pk>/', SnippetUpdateAPI.as_view()),
    path('delete/', SnippetDeleteAPI.as_view()),
    path('tags/list/', TagListAPI.as_view()),
    path('tags/<int:tag_id>/snippets/', SnippetsByTagAPI.as_view(), name='snippets-by-tag'),
]