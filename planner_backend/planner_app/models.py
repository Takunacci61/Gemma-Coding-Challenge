from django.db import models
from django.contrib.auth.models import User


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
        ('Weekday', 'Weekday'),
        ('Weekend', 'Weekend'),
    )
    days_of_week = models.CharField(max_length=20, choices=DAYS_OF_WEEK_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.activity_name} ({self.start_time} - {self.end_time})"


# User Goal model


class Goal(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Expired', 'Expired'),
        ('Cancelled', 'Cancelled'),
        ('In Progress', 'In Progress'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_name = models.CharField(max_length=100)
    goal_description = models.TextField()
    goal_start_date = models.DateField()
    goal_end_date = models.DateField()
    model_notes = models.TextField(null=True, blank=True)
    feasibility_score = models.IntegerField(default=0)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')

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


class DailyPlanActivity(models.Model):
    plan = models.ForeignKey(DailyPlan, on_delete=models.CASCADE, related_name='activities')
    activity_name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.activity_name} ({self.status})"

