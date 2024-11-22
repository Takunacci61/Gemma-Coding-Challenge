from django.contrib import admin
from .models import *


@admin.register(DailyRoutine)
class DailyRoutineAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_name', 'start_time', 'end_time', 'days_of_week')
    list_filter = ('days_of_week',)
    search_fields = ('user__username', 'activity_name')


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_name', 'goal_start_date', 'goal_end_date', 'feasibility_score')
    search_fields = ('goal_name', 'user__username')
    list_filter = ('goal_start_date', 'goal_end_date')


# Inline model for DailyPlanActivity
class DailyPlanActivityInline(admin.TabularInline):  # You can also use admin.StackedInline
    model = DailyPlanActivity
    extra = 1  # Number of blank forms for new activities


@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_date', 'goal', 'status', 'day_number_display')
    list_filter = ('status', 'plan_date', 'goal__goal_name')
    search_fields = ('goal__goal_name', 'plan_date')
    ordering = ('plan_date',)
    date_hierarchy = 'plan_date'
    inlines = [DailyPlanActivityInline]  # Add the inline model here

    def day_number_display(self, obj):
        """
        Display the day number in the admin panel.
        """
        return obj.day_number or "N/A"

    day_number_display.short_description = "Day Number"


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
        updated = queryset.update(status='Completed')
        self.message_user(request, f"{updated} activities marked as completed.")

    mark_completed.short_description = "Mark selected activities as Completed"


@admin.register(UnplannedActivity)
class UnplannedActivityAdmin(admin.ModelAdmin):
    list_display = ('goal', 'activity_date', 'activity_name', 'start_time', 'end_time', 'effect')
    list_filter = ('effect', 'activity_date')
    search_fields = ('activity_name', 'goal__goal_name')


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('goal', 'report_date', 'model_notes', 'user_notes')
    search_fields = ('goal__goal_name',)
    list_filter = ('report_date',)


@admin.register(GoalReport)
class GoalReportAdmin(admin.ModelAdmin):
    list_display = ('goal', 'completion_rate', 'report_date')
    search_fields = ('goal__goal_name',)
    list_filter = ('report_date',)
