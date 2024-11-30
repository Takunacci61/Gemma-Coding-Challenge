from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import NotificationViewSet, UserProfileView, RegisterViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')
router.register('register', RegisterViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('user-profile/', UserProfileView.as_view(), name='user-profile'),
]

