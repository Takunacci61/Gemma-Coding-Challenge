import re
import json
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter goals for the logged-in user
        return DailyRoutine.objects.filter(user=self.request.user)


class DailyPlanViewSet(viewsets.ModelViewSet):
    queryset = DailyPlan.objects.all()
    serializer_class = DailyPlanSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        # Filter goals for the logged-in user
        return DailyPlan.objects.filter(user=self.request.user)


class DailyPlanActivityViewSet(viewsets.ModelViewSet):
    queryset = DailyPlanActivity.objects.all()
    serializer_class = DailyPlanActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter goals for the logged-in user
        return DailyPlanActivity.objects.filter(user=self.request.user)


class UnplannedActivityViewSet(viewsets.ModelViewSet):
    queryset = UnplannedActivity.objects.all()
    serializer_class = UnplannedActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter goals for the logged-in user
        return UnplannedActivity.objects.filter(user=self.request.user)


class DailyReportViewSet(viewsets.ModelViewSet):
    queryset = DailyReport.objects.all()
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter goals for the logged-in user
        return DailyReport.objects.filter(user=self.request.user)


class GoalReportViewSet(viewsets.ModelViewSet):
    queryset = GoalReport.objects.all()
    serializer_class = GoalReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter goals for the logged-in user
        return GoalReport.objects.filter(user=self.request.user)


# Generate Daily Plan

class GenerateDailyPlanAPIView(APIView):
    """
    Endpoint to generate a daily plan and activities for a specific goal,
    only if one does not already exist for the day.
    """

    def post(self, request, goal_id):
        try:
            # Fetch the goal
            goal = Goal.objects.get(id=goal_id, user=request.user)

            # Check if a daily plan already exists for today
            today = timezone.now().date()
            if DailyPlan.objects.filter(goal=goal, plan_date=today).exists():
                return Response(
                    {"message": "A daily plan for this goal already exists for today."},
                    status=status.HTTP_200_OK
                )

            # Check if the goal is within the valid date range
            if not (goal.goal_start_date <= today <= goal.goal_end_date):
                return Response(
                    {"error": "Goal is not active on the current date."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch existing progress
            daily_plans = DailyPlan.objects.filter(goal=goal, plan_date__lt=today).order_by('plan_date')
            completed_activities_count = DailyPlanActivity.objects.filter(
                plan__goal=goal,
                status='Completed'
            ).count()

            # Prepare previous plans and progress data
            previous_plans_data = []
            for plan in daily_plans:
                activities = plan.activities.all()
                activities_data = []
                for activity in activities:
                    activities_data.append({
                        "activity_name": activity.activity_name,
                        "start_time": activity.start_time.strftime("%H:%M"),
                        "end_time": activity.end_time.strftime("%H:%M"),
                        "status": activity.status
                    })
                previous_plans_data.append({
                    "plan_date": plan.plan_date.strftime("%Y-%m-%d"),
                    "status": plan.status,
                    "activities": activities_data
                })

            # Prepare input for the AI model
            input_content = (
                f"Based on the following goal and progress, generate a daily plan for today with activities. "
                f"Goal Name: '{goal.goal_name}'. "
                f"Goal Description: '{goal.goal_description}'. "
                f"Goal Start Date: {goal.goal_start_date}. "
                f"Goal End Date: {goal.goal_end_date}. "
                f"Completed Activities So Far: {completed_activities_count}. "
                f"Previous Plans and Progress: {json.dumps(previous_plans_data)}. "
                f"Your response must be valid JSON only, with the following structure:\n"
                f"{{\n"
                f"  \"notes\": \"string\",\n"
                f"  \"activities\": [\n"
                f"    {{\n"
                f"      \"activity_name\": \"string\",\n"
                f"      \"start_time\": \"HH:MM\" (24-hour format),\n"
                f"      \"end_time\": \"HH:MM\" (24-hour format),\n"
                f"      \"notes\": \"string\"\n"
                f"    }},\n"
                f"    ...\n"
                f"  ]\n"
                f"}}\n"
                f"Ensure that 'start_time' and 'end_time' are valid times in 24-hour format (HH:MM). "
                f"If generating a plan for today, ensure that 'start_time' is greater than the current time ({timezone.now().strftime('%H:%M')}). "
                f"Do not include any explanation or additional text. Only output the JSON data."
            )

            input_data = {
                "role": "user",
                "content": input_content
            }

            # Initialize the OpenAI client
            client = OpenAI(
                base_url=settings.GEMMA_BASE_URL,
                api_key=settings.GEMMA_API_KEY
            )

            # Call the AI model with a timeout
            completion = client.chat.completions.create(
                model="google/gemma-2-27b-it",
                messages=[input_data],
                timeout=15  # Set a timeout to prevent long waits
            )

            # Get the AI response
            response_text = completion.choices[0].message.content.strip()
            logger.info(f"Gemma AI response: {response_text}")

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_content = json_match.group(0)
                daily_plan_data = json.loads(json_content)
            else:
                logger.error("No JSON content found in AI response.")
                return Response(
                    {"error": "Failed to parse AI response. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Create today's daily plan
            daily_plan = DailyPlan.objects.create(
                goal=goal,
                plan_date=today,
                status='Pending',
                notes=daily_plan_data.get("notes", "")
            )

            # Prepare activity instances for bulk creation
            activities = daily_plan_data.get("activities", [])
            activity_instances = []
            time_format = "%H:%M"
            current_time = timezone.now().time()
            for activity in activities:
                try:
                    # Parse and validate start_time and end_time
                    start_time_str = activity["start_time"]
                    end_time_str = activity["end_time"]
                    start_time_obj = datetime.strptime(start_time_str, time_format).time()
                    end_time_obj = datetime.strptime(end_time_str, time_format).time()

                    # Ensure start_time is before end_time
                    if start_time_obj >= end_time_obj:
                        logger.error(
                            f"Start time {start_time_obj} is not before end time {end_time_obj} in activity '{activity['activity_name']}'")
                        continue  # Skip invalid activity

                    # If plan date is today, ensure start_time is after current time
                    if daily_plan.plan_date == today and start_time_obj <= current_time:
                        logger.error(
                            f"Start time {start_time_obj} is not after current time {current_time} in activity '{activity['activity_name']}'")
                        continue  # Skip activity that has already passed

                    activity_instances.append(DailyPlanActivity(
                        plan=daily_plan,
                        activity_name=activity["activity_name"],
                        start_time=start_time_obj,
                        end_time=end_time_obj,
                        notes=activity.get("notes", ""),
                        status='Pending'
                    ))
                except (KeyError, ValueError) as e:
                    logger.error(f"Error parsing activity data: {e}")
                    continue  # Skip invalid activity

            if not activity_instances:
                logger.error("No valid activities to create.")
                return Response(
                    {"error": "No valid activities were generated. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Bulk create activities
            DailyPlanActivity.objects.bulk_create(activity_instances)

            return Response(
                {"message": "Daily plan and activities created successfully.", "plan_id": daily_plan.id},
                status=status.HTTP_201_CREATED
            )

        except Goal.DoesNotExist:
            return Response(
                {"error": "Goal not found or not accessible."},
                status=status.HTTP_404_NOT_FOUND
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from AI: {e}")
            logger.error(f"AI response was: {response_text}")
            return Response(
                {"error": "Failed to parse AI response. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.error(f"Error generating daily plan: {e}")
            return Response(
                {"error": "Failed to generate daily plan. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
