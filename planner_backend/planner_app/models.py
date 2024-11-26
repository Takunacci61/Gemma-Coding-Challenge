from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timedelta
import openai


# Daily Routine
class DailyRoutine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_routines')
    activity_name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    DAYS_OF_WEEK_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )
    days_of_week = models.CharField(max_length=20, choices=DAYS_OF_WEEK_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.activity_name} ({self.start_time} - {self.end_time})"


# User Goal model

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_name = models.CharField(max_length=100)
    goal_description = models.TextField()
    goal_start_date = models.DateField()
    goal_end_date = models.DateField()
    feasibility_score = models.IntegerField(default=0)

    def calculate_feasibility_score(self):
        """
        Calls Gemma AI to analyze goal feasibility.
        Returns a score between 1 and 10.
        """
        try:
            client = openai.OpenAI(
                base_url=settings.GEMMA_BASE_URL,
                api_key=settings.GEMMA_API_KEY
            )

            # Prepare the input for the AI model
            input_data = {
                "role": "user",
                "content": (
                    f"Goal Name: '{self.goal_name}'. "
                    f"Analyze this goal for feasibility: '{self.goal_description}'. "
                    f"The goal is to be completed in {self.goal_end_date - self.goal_start_date} days. "
                    f"Rate its feasibility on a scale of 1 to 10, with 10 being very feasible. "
                    f"Respond with only a single integer number between 1 and 10, inclusive, and no other text or special characters."
                )
            }

            # Call Gemma AI model
            completion = client.chat.completions.create(
                model="google/gemma-2-27b-it",
                messages=[input_data]
            )

            # Parse the response
            response = completion.choices[0].message.content.strip()

            print(f"Gemma AI response: {response}")

            # Ensure the score is an integer between 1 and 10
            score = int(response)
            return max(1, min(score, 10))  # Clamp score between 1 and 10

        except Exception as e:
            # Handle errors and set a fallback score
            print(f"Error calling Gemma AI: {e}")
            return 5  # Default fallback score

    def save(self, *args, **kwargs):
        # Ensure goal period does not exceed 30 days
        if (self.goal_end_date - self.goal_start_date).days > 30:
            raise ValueError("Goal period cannot exceed 30 days.")

        # Calculate the feasibility score using Gemma AI
        self.feasibility_score = self.calculate_feasibility_score()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.goal_name


# Daily Plan model

class DailyPlan(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('In Progress', 'In Progress'),
        ('Skipped', 'Skipped'),
    )

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='daily_plans')
    plan_date = models.DateField()
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    @property
    def day_number(self):
        """
        Calculate the day number of the plan relative to the goal's start date.
        """
        if self.goal.goal_start_date and self.plan_date:
            day_number = (self.plan_date - self.goal.goal_start_date).days + 1
            if day_number < 1 or day_number > (self.goal.goal_end_date - self.goal.goal_start_date).days + 1:
                return None  # Out of range for the goal period
            return day_number
        return None  # Missing goal_start_date or plan_date

    def __str__(self):
        return f"{self.goal.goal_name} - {self.plan_date}"


class DailyPlanActivity(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Skipped', 'Skipped'),
    )

    plan = models.ForeignKey(DailyPlan, on_delete=models.CASCADE, related_name='activities')
    activity_name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.activity_name} ({self.status})"


# Unplanned Activity model

class UnplannedActivity(models.Model):
    EFFECT_CHOICES = (
        ('Adjust', 'Adjust'),
        ('Dismiss', 'Dismiss'),
    )

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='unplanned_activities')
    activity_date = models.DateField()
    activity_name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.TextField(null=True, blank=True)
    effect = models.CharField(max_length=50, choices=EFFECT_CHOICES)

    def __str__(self):
        return self.activity_name


# Daily Report model

class DailyReport(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='daily_report')
    model_notes = models.TextField(null=True, blank=True)
    user_notes = models.TextField(null=True, blank=True)
    report_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.report_date} for {self.goal.goal_name}"


# Goal Report model

class GoalReport(models.Model):
    goal = models.OneToOneField(Goal, on_delete=models.CASCADE, related_name='goal_report')
    model_notes = models.TextField(null=True, blank=True)
    user_notes = models.TextField(null=True, blank=True)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    report_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Goal Report for {self.goal.goal_name}"


