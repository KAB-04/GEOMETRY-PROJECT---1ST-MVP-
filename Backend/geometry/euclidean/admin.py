from django.contrib import admin

from .models import SolvedProblem


@admin.register(SolvedProblem)
class SolvedProblemAdmin(admin.ModelAdmin):
    list_display = ("id", "operation", "dimension", "created_at")
    search_fields = ("question", "operation", "operation_label")
    list_filter = ("dimension", "operation", "created_at")
