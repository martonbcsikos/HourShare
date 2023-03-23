from django.contrib import admin

from .models import SSLHour


@admin.register(SSLHour)
class SSLHourAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "student_id",
        "date_earned",
        "hours",
        "project_name",
        "school_name",
        "club",
    )
