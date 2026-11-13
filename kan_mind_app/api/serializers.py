from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from ..models import Board, Comment, Task
from .permissions import is_board_member

User = get_user_model()


def user_fullname(user):
    """Return the display name expected by the frontend."""
    return user.get_full_name().strip() or user.username


class UserSummarySerializer(serializers.ModelSerializer):
    """Serialize the user shape used throughout the KanMind API."""

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return user_fullname(obj)


class RegistrationSerializer(serializers.Serializer):
    """Validate and create a KanMind user."""

    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match.'}
            )
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        return User.objects.create_user(
            username=email,
            email=email,
            first_name=validated_data['fullname'].strip(),
            password=validated_data['password'],
        )


class LoginSerializer(serializers.Serializer):
    """Validate email and password credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = User.objects.filter(email__iexact=attrs['email']).first()
        if not user or not user.check_password(attrs['password']):
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('User account is inactive.')
        attrs['user'] = user
        return attrs


class AuthResponseSerializer(serializers.Serializer):
    """Serialize the flat authentication response required by KanMind."""

    token = serializers.CharField()
    fullname = serializers.CharField()
    email = serializers.EmailField()
    user_id = serializers.IntegerField()


class BoardListSerializer(serializers.ModelSerializer):
    """Serialize board list and creation responses."""

    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
        ]


class BoardCreateSerializer(serializers.ModelSerializer):
    """Validate board creation input."""

    class Meta:
        model = Board
        fields = ['title', 'members']


class TaskPersonMixin(serializers.Serializer):
    """Provide nested assignee and reviewer representations."""

    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)


class TaskBoardSerializer(TaskPersonMixin, serializers.ModelSerializer):
    """Serialize tasks embedded in board details."""

    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count',
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serialize a board together with members and tasks."""

    owner_id = serializers.IntegerField(read_only=True)
    members = UserSummarySerializer(many=True, read_only=True)
    tasks = TaskBoardSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Validate board title and member replacement."""

    class Meta:
        model = Board
        fields = ['title', 'members']
        extra_kwargs = {
            'title': {'required': False},
            'members': {'required': False},
        }


class BoardUpdateResponseSerializer(serializers.ModelSerializer):
    """Serialize the board PATCH response."""

    owner_data = UserSummarySerializer(source='owner', read_only=True)
    members_data = UserSummarySerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']


class TaskWriteSerializer(serializers.ModelSerializer):
    """Validate task creation and updates."""

    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee', queryset=User.objects.all(),
        allow_null=True, required=False, write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer', queryset=User.objects.all(),
        allow_null=True, required=False, write_only=True,
    )

    class Meta:
        model = Task
        fields = [
            'board', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'due_date',
        ]

    def validate_board(self, board):
        if self.instance:
            raise serializers.ValidationError('Board cannot be changed.')
        if not is_board_member(self.context['request'].user, board):
            raise serializers.ValidationError('Board access denied.')
        return board

    def validate(self, attrs):
        board = attrs.get('board') or self.instance.board
        self._validate_member(attrs.get('assignee'), board, 'assignee_id')
        self._validate_member(attrs.get('reviewer'), board, 'reviewer_id')
        return attrs

    @staticmethod
    def _validate_member(user, board, field):
        if user is None:
            return
        if not is_board_member(user, board):
            raise serializers.ValidationError(
                {field: 'User must be a board member.'}
            )


class TaskDashboardSerializer(TaskPersonMixin, serializers.ModelSerializer):
    """Serialize task create and dashboard responses."""

    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count',
        ]


class TaskUpdateResponseSerializer(TaskPersonMixin, serializers.ModelSerializer):
    """Serialize the task PATCH response."""

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date',
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Serialize nested task comments."""

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        return user_fullname(obj.author)
