from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Board, Comment, Task

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    """Serialize public user fields required by API responses."""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class RegistrationSerializer(serializers.Serializer):
    """Validate and create a user using the email address as login name."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
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
            password=validated_data['password'],
        )


class LoginSerializer(serializers.Serializer):
    """Validate email/password credentials for token authentication."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = User.objects.filter(email__iexact=attrs['email']).first()
        if not user or not user.check_password(attrs['password']):
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This user account is inactive.')
        attrs['user'] = user
        return attrs


class BoardSerializer(serializers.ModelSerializer):
    """Serialize boards and keep ownership controlled by the request user."""

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

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
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serialize tasks and validate board-related assignments."""

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
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        board = attrs.get('board') or getattr(self.instance, 'board', None)
        request = self.context.get('request')
        if request and board and not self._can_access_board(request.user, board):
            raise serializers.ValidationError({'board': 'Board access denied.'})
        assignee = attrs.get('assignee', getattr(self.instance, 'assignee', None))
        reviewer = attrs.get('reviewer', getattr(self.instance, 'reviewer', None))
        self._validate_board_user(assignee, board, 'assignee')
        self._validate_board_user(reviewer, board, 'reviewer')
        return attrs

    @staticmethod
    def _can_access_board(user, board):
        return board.owner_id == user.id or board.members.filter(pk=user.pk).exists()

    @staticmethod
    def _validate_board_user(user, board, field):
        if user is None or board is None:
            return
        is_member = board.owner_id == user.id or board.members.filter(pk=user.pk).exists()
        if not is_member:
            raise serializers.ValidationError(
                {field: 'User must be a member of the selected board.'}
            )


class CommentSerializer(serializers.ModelSerializer):
    """Serialize task comments and assign authors through the request."""

    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def validate_task(self, task):
        request = self.context.get('request')
        if not request:
            return task
        board = task.board
        has_access = board.owner_id == request.user.id
        has_access = has_access or board.members.filter(pk=request.user.pk).exists()
        if not has_access:
            raise serializers.ValidationError('Task access denied.')
        return task
