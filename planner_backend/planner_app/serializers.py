from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DailyRoutine, Goal, DailyPlan, UnplannedActivity, DailyReport, GoalReport, DailyPlanActivity


# DailyRoutine Serializer
class DailyRoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRoutine
        fields = ['id', 'user', 'activity_name', 'start_time', 'end_time', 'days_of_week']


# Goal Serializer
class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'user', 'goal_name', 'goal_description', 'goal_start_date', 'goal_end_date',
                  'feasibility_score']


class DailyPlanActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPlanActivity
        fields = ['id', 'plan', 'activity_name', 'start_time', 'end_time', 'status', 'notes', ]


class DailyPlanSerializer(serializers.ModelSerializer):
    activities = DailyPlanActivitySerializer(many=True, read_only=True, source='activities')

    class Meta:
        model = DailyPlan
        fields = ['id', 'goal', 'plan_date', 'notes', 'status', 'day_number',
                  'activities']


# UnplannedActivity Serializer
class UnplannedActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UnplannedActivity
        fields = ['id', 'goal', 'activity_date', 'activity_name', 'start_time', 'end_time', 'reason', 'effect']


# DailyReport Serializer
class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReport
        fields = ['id', 'goal', 'model_notes', 'user_notes', 'report_date']


# GoalReport Serializer
class GoalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalReport
        fields = ['id', 'goal', 'model_notes', 'user_notes', 'completion_rate', 'report_date']
