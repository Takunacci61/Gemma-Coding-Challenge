from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DailyRoutineViewSet, GoalViewSet, DailyPlanViewSet,
    DailyPlanActivityViewSet, UnplannedActivityViewSet,
    DailyReportViewSet, GoalReportViewSet, GenerateDailyPlanAPIView, RecentGoalView
)

router = DefaultRouter()
router.register('daily-routines', DailyRoutineViewSet, basename='dailyroutine')
router.register('goals', GoalViewSet, basename='goal')
router.register('daily-plans', DailyPlanViewSet, basename='dailyplan')
router.register('daily-plan-activities', DailyPlanActivityViewSet, basename='dailyplanactivity')
router.register('unplanned-activities', UnplannedActivityViewSet, basename='unplannedactivity')
router.register('daily-reports', DailyReportViewSet, basename='dailyreport')
router.register('goal-reports', GoalReportViewSet, basename='goalreport')

urlpatterns = [
    path('', include(router.urls)),  # Include router URLs
    path('generate-daily-plan/<int:goal_id>/', GenerateDailyPlanAPIView.as_view(), name='generate_daily_plan'),
    path('goals/recent/for-user/', RecentGoalView.as_view(), name='recent-goal'),
]

