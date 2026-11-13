from django.contrib import admin

from .models import Board, Comment, Task


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Configure board administration."""

    list_display = ('id', 'title', 'owner', 'created_at', 'updated_at')
    search_fields = ('title', 'owner__username', 'owner__email')
    filter_horizontal = ('members',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configure task administration."""

    list_display = (
        'id',
        'title',
        'board',
        'status',
        'priority',
        'assignee',
        'reviewer',
        'due_date',
    )
    list_filter = ('status', 'priority', 'board')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Configure comment administration."""

    list_display = ('id', 'task', 'author', 'created_at')
    search_fields = ('content', 'author__username', 'author__email')
    readonly_fields = ('created_at',)
