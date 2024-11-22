from rest_framework import viewsets
from .models import Notification, UserProfile
from .serializers import UserProfileSerializer, NotificationSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action


# Custom Token for JWT Authentication

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# User Profile Endpoints

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return the profile of the logged-in user only
        return UserProfile.objects.filter(user=self.request.user)


# Notification Endpoints

class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        # Filter goals for the logged-in user
        return Notification.objects.filter(user=self.request.user)
