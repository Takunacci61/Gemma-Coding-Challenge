from django.contrib import admin
from .models import *
from django.core.exceptions import ValidationError
from django.contrib import messages


@admin.register(DailyRoutine)
class DailyRoutineAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_name', 'start_time', 'end_time', 'days_of_week')
    list_filter = ('days_of_week',)
    search_fields = ('user__username', 'activity_name')


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('goal_name', 'user', 'status', 'goal_start_date', 'goal_end_date', 'feasibility_score')
    list_filter = ('status', 'goal_start_date', 'goal_end_date')
    search_fields = ('goal_name', 'user__username')
    ordering = ('-goal_start_date',)

    def save_model(self, request, obj, form, change):
        """
        Overrides save_model to handle ValidationError gracefully.
        """
        try:
            obj.save()
        except ValidationError as e:
            self.message_user(request, f"Error: {e.message}", level=messages.ERROR)
        else:
            self.message_user(request, "Goal saved successfully.", level=messages.SUCCESS)


# Inline model for DailyPlanActivity
class DailyPlanActivityInline(admin.TabularInline):
    model = DailyPlanActivity
    extra = 1  # Number of blank forms for new activities


@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    list_display = ('goal', 'plan_date', 'status', 'day_number')
    list_filter = ('status', 'plan_date')
    search_fields = ('goal__goal_name', 'goal__user__username')
    inlines = [DailyPlanActivityInline]  # Added to display activities inline with the plan

    def save_model(self, request, obj, form, change):
        """
        Overrides save_model to handle ValidationError gracefully.
        """
        try:
            obj.save()
        except ValidationError as e:
            # Add a user-friendly error message to the admin interface
            self.message_user(request, f"Error: {e.message}", level=messages.ERROR)
        else:
            # Add a success message if the save was successful
            self.message_user(request, "Daily plan saved successfully.", level=messages.SUCCESS)


@admin.register(DailyPlanActivity)
class DailyPlanActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_name', 'plan', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'plan__plan_date')
    search_fields = ('activity_name', 'plan__activity_name')
    ordering = ('plan__plan_date', 'start_time')

    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        """
        Custom action to mark selected activities as completed.
        """
        updated = queryset.update(status=True)
        self.message_user(request, f"{updated} activities marked as completed.")

    mark_completed.short_description = "Mark selected activities as Completed"

