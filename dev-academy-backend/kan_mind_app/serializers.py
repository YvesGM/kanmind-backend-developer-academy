from rest_framework import serializers

from .models import Board, Comment, Task


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner',
            'members',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'board',
            'assignee',
            'reviewer',
            'status',
            'priority',
            'due_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'task',
            'author',
            'content',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
        ]