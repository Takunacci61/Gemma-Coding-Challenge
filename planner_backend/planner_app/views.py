from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated


# User Goal model

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

    def get_queryset(self):
        # Filter goals for the logged-in user
        return Goal.objects.filter(user=self.request.user)


class DailyRoutineViewSet(viewsets.ModelViewSet):
    queryset = DailyRoutine.objects.all()
    serializer_class = DailyRoutineSerializer

    def get_queryset(self):
        # Filter goals for the logged-in user
        return DailyRoutine.objects.filter(user=self.request.user)


class DailyPlanViewSet(viewsets.ModelViewSet):
    queryset = DailyPlan.objects.all()
    serializer_class = DailyPlanSerializer

    def get_queryset(self):
        # Filter goals for the logged-in user
        return DailyPlan.objects.filter(user=self.request.user)


class DailyPlanActivityViewSet(viewsets.ModelViewSet):
    queryset = DailyPlanActivity.objects.all()
    serializer_class = DailyPlanActivitySerializer

    def get_queryset(self):
        # Filter goals for the logged-in user
        return DailyPlanActivity.objects.filter(user=self.request.user)


class UnplannedActivityViewSet(viewsets.ModelViewSet):
    queryset = UnplannedActivity.objects.all()
    serializer_class = UnplannedActivitySerializer

    def get_queryset(self):
        # Filter goals for the logged-in user
        return UnplannedActivity.objects.filter(user=self.request.user)


class DailyReportViewSet(viewsets.ModelViewSet):
    queryset = DailyReport.objects.all()
    serializer_class = DailyReportSerializer

    def get_queryset(self):
        # Filter goals for the logged-in user
        return DailyReport.objects.filter(user=self.request.user)


class GoalReportViewSet(viewsets.ModelViewSet):
    queryset = GoalReport.objects.all()
    serializer_class = GoalReportSerializer

    def get_queryset(self):
        # Filter goals for the logged-in user
        return GoalReport.objects.filter(user=self.request.user)
