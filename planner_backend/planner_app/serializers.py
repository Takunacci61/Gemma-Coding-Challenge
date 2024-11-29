from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date
from .models import DailyRoutine, Goal, DailyPlan, UnplannedActivity, DailyReport, GoalReport, DailyPlanActivity
from django.core.exceptions import ValidationError
from django.utils.timezone import now


# DailyRoutine Serializer
class DailyRoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRoutine
        fields = ['id', 'user', 'activity_name', 'start_time', 'end_time', 'days_of_week']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        # Set the user to the logged-in user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


# Goal Serializer
class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        read_only_fields = ['user', 'status', 'feasibility_score', 'model_notes']
        fields = '__all__'

    def validate(self, data):
        """
        Custom validation for Goal creation.
        """
        # Get the current user from the context
        user = self.context['request'].user

        # Ensure the user doesn't already have a 'Pending' or 'In Progress' goal
        if Goal.objects.filter(user=user, status__in=['Pending', 'In Progress']).exists():
            raise serializers.ValidationError(
                "You cannot create a new goal while you have a goal in 'Pending' or 'In Progress' status."
            )

        # Validate that the goal period does not exceed 30 days
        goal_start_date = data.get('goal_start_date')
        goal_end_date = data.get('goal_end_date')
        if goal_start_date and goal_end_date and (goal_end_date - goal_start_date).days > 30:
            raise serializers.ValidationError(
                "The goal period cannot exceed 30 days."
            )

        # Validate that the start date is not in the past
        if goal_start_date and goal_start_date < date.today():
            raise serializers.ValidationError(
                "The goal start date cannot be in the past."
            )

        return data

    def create(self, validated_data):
        """
        Automatically set the user to the currently logged-in user.
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class DailyPlanActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPlanActivity
        fields = ['id', 'plan', 'activity_name', 'start_time', 'end_time', 'status', 'notes', ]


class DailyPlanSerializer(serializers.ModelSerializer):
    activities = DailyPlanActivitySerializer(many=True, read_only=True)

    class Meta:
        model = DailyPlan
        fields = ['id', 'goal', 'plan_date', 'notes', 'status', 'day_number', 'activities']

    def validate(self, data):
        """
        Custom validation for DailyPlan.
        """
        goal = data.get('goal')
        plan_date = data.get('plan_date')

        # Validate that the goal is in 'Pending' or 'In Progress' state
        if goal.status not in ['Pending', 'In Progress']:
            raise serializers.ValidationError(
                "A daily plan can only be created if the associated goal is in 'Pending' or 'In Progress' state."
            )

        # Validate that the plan date falls within the goal's start and end dates
        if plan_date:
            if plan_date < goal.goal_start_date or plan_date > goal.goal_end_date:
                raise serializers.ValidationError("The plan date must be within the goal's start and end dates.")

        return data


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


# Recent Goal Serializer
class RecentGoalSerializer(serializers.ModelSerializer):
    daily_plans = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = '__all__'

    def get_daily_plans(self, obj):
        """
        Return only the daily plan for the current day.
        """
        today = now().date()
        daily_plan = obj.daily_plans.filter(plan_date=today).first()  # Fetch today's daily plan if it exists
        if daily_plan:
            return DailyPlanSerializer(daily_plan).data
        return None
