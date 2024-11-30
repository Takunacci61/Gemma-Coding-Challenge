from rest_framework import serializers
from datetime import date
from .models import DailyRoutine, Goal, DailyPlan, DailyPlanActivity
from django.utils.timezone import now
from django.conf import settings
import openai


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
        Add feasibility score and motivational notes.
        """
        user = self.context['request'].user
        validated_data['user'] = user

        # Call Gemma AI to calculate feasibility score and generate notes
        goal = super().create(validated_data)
        goal.feasibility_score = self.calculate_feasibility_score(goal)
        goal.model_notes = self.generate_model_notes(goal)
        goal.save()
        return goal

    def calculate_feasibility_score(self, goal):
        """
        Calls Gemma AI to analyze goal feasibility.
        """
        try:
            client = openai.OpenAI(
                base_url=settings.GEMMA_BASE_URL,
                api_key=settings.GEMMA_API_KEY
            )

            input_data = {
                "role": "user",
                "content": (
                    f"Please analyze the following goal for feasibility:\n"
                    f"Goal Name: {goal.goal_name}\n"
                    f"Goal Description: {goal.goal_description}\n"
                    f"Timeframe: {(goal.goal_end_date - goal.goal_start_date).days} days\n"
                    f"On a scale of 1 to 10 (1 being least feasible, 10 being most feasible), rate its feasibility.\n"
                    f"Respond with only a single number between 1 and 10."
                )
            }

            completion = client.chat.completions.create(
                model="google/gemma-2-27b-it",
                messages=[input_data]
            )

            response = completion.choices[0].message.content.strip()
            score = int(response)
            return max(1, min(score, 10))  # Clamp score between 1 and 10
        except Exception as e:
            print(f"Error calling Gemma AI: {e}")
            return 5  # Default fallback score

    def generate_model_notes(self, goal):
        """
        Generate motivational notes for the goal.
        """
        try:
            client = openai.OpenAI(
                base_url=settings.GEMMA_BASE_URL,
                api_key=settings.GEMMA_API_KEY
            )

            input_data = {
                "role": "user",
                "content": (
                    f"Please write a motivational paragraph to encourage someone working towards the following goal:\n"
                    f"Goal Name: {goal.goal_name}\n"
                    f"Goal Description: {goal.goal_description}"
                )
            }

            completion = client.chat.completions.create(
                model="google/gemma-2-27b-it",
                messages=[input_data]
            )

            response = completion.choices[0].message.content.strip()
            return response[:100]  # Ensure the text is within 100 words
        except Exception as e:
            print(f"Error generating motivational notes: {e}")
            return (
                "Keep going! Your goal is a beautiful journey of growth and discovery. "
                "Every small step forward is a victory worth celebrating."
            )


class DailyPlanActivityStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPlanActivity
        fields = ['id', 'status']


class DailyPlanActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPlanActivity
        fields = ['id', 'plan', 'activity_name', 'start_time', 'end_time', 'status', 'notes', ]


class DailyPlanActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPlanActivity
        fields = ['id', 'activity_name', 'start_time', 'end_time', 'status', 'notes']


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

        # Calculate day number
        day_number = (plan_date - goal.goal_start_date).days + 1
        if day_number < 1 or day_number > (goal.goal_end_date - goal.goal_start_date).days + 1:
            raise serializers.ValidationError("The plan date is out of range for the goal's period.")

        return data

    def create(self, validated_data):
        """
        Override the create method to handle goal status update and notes generation.
        """
        goal = validated_data.get('goal')
        notes = validated_data.get('notes')

        # Update goal status to 'In Progress' if it is currently 'Pending'
        if goal.status == 'Pending':
            goal.status = 'In Progress'
            goal.save()

        # Generate motivational notes if not already provided
        if not notes:
            validated_data['notes'] = self.generate_motivational_quote()

        return super().create(validated_data)

    def generate_motivational_quote(self):
        """
        Generate a motivational quote using the Gemma AI model.
        """
        try:

            # Initialize OpenAI API client
            client = openai.OpenAI(
                base_url=settings.GEMMA_BASE_URL,
                api_key=settings.GEMMA_API_KEY
            )

            # Prepare the input for the AI model
            input_data = {
                "role": "user",
                "content": (
                    "Generate a motivational quote that is playful, encouraging, "
                    "and less than 50 words. It should inspire someone to achieve their daily plan."
                )
            }

            # Call the Gemma AI model
            completion = client.chat.completions.create(
                model="google/gemma-2-27b-it",
                messages=[input_data]
            )

            # Parse and return the response
            quote = completion.choices[0].message.content.strip()
            return quote

        except Exception as e:
            # Handle errors and provide a fallback quote
            print(f"Error generating motivational quote: {e}")
            return "Keep pushing forward—you're closer to success than you think!"


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
