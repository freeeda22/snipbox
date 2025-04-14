from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserCreateAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('edit/<int:pk>/', UserUpdateAPIView.as_view()),
    path('delete/<int:id>/', UserDeleteAPIView.as_view()),
    path('detail/<int:id>/', UserRetrieveAPIView.as_view()),
]