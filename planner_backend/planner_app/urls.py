from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyRoutineViewSet, GoalViewSet,GenerateDailyPlanAPIView, RecentGoalView, DailyPlanActivityViewSet


router = DefaultRouter()
router.register('daily-routines', DailyRoutineViewSet, basename='dailyroutine')
router.register('goals', GoalViewSet, basename='goal')
router.register('daily-plan-activities-update', DailyPlanActivityViewSet, basename='daily-plan-activity-update')

urlpatterns = [
    path('', include(router.urls)),  # Include router URLs
    path('generate-daily-plan/<int:goal_id>/', GenerateDailyPlanAPIView.as_view(), name='generate_daily_plan'),
    path('goals/recent/for-user/', RecentGoalView.as_view(), name='recent-goal'),
]

