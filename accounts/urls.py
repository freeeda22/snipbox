from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserCreateAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
]