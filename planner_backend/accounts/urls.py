from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, UserProfileViewSet


router = DefaultRouter()
router.register('user-profiles', UserProfileViewSet, basename='userprofile')
router.register('notifications', NotificationViewSet, basename='notification')
urlpatterns = router.urls

