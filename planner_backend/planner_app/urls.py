from rest_framework.routers import DefaultRouter
from .views import DailyRoutineViewSet, GoalViewSet, DailyPlanViewSet, UnplannedActivityViewSet, DailyReportViewSet,\
    GoalReportViewSet, DailyPlanActivityViewSet


router = DefaultRouter()
router.register('daily-routines', DailyRoutineViewSet, basename='dailyroutine')
router.register('goals', GoalViewSet, basename='goal')
router.register('daily-plans', DailyPlanViewSet, basename='dailyplan')
router.register('daily-plan-activities', DailyPlanActivityViewSet)
router.register('unplanned-activities', UnplannedActivityViewSet, basename='unplannedactivity')
router.register('daily-reports', DailyReportViewSet, basename='dailyreport')
router.register('goal-reports', GoalReportViewSet, basename='goalreport')


urlpatterns = router.urls
