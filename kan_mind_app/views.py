from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Board, Comment, Task
from .permissions import (
    BoardAccessPermission,
    RelatedBoardMemberPermission,
    is_board_member,
)
from .serializers import (
    BoardSerializer,
    CommentSerializer,
    LoginSerializer,
    RegistrationSerializer,
    TaskSerializer,
    UserSummarySerializer,
)

User = get_user_model()


class RegistrationView(APIView):
    """Create a user and return an authentication token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'user': UserSummarySerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate a user by email and return a token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSummarySerializer(user).data})


class LogoutView(APIView):
    """Invalidate the current user's token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCheckView(APIView):
    """Return whether an email address already exists."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = str(request.data.get('email', '')).strip()
        if not email:
            return Response(
                {'email': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        exists = User.objects.filter(email__iexact=email).exists()
        return Response({'exists': exists})


class BoardListCreateView(generics.ListCreateAPIView):
    """List accessible boards or create a board owned by the request user."""

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Board.objects.filter(
                Q(owner=self.request.user) | Q(members=self.request.user)
            )
            .select_related('owner')
            .prefetch_related('members')
            .distinct()
        )

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve a board; only its owner may update or delete it."""

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, BoardAccessPermission]

    def get_queryset(self):
        return (
            Board.objects.filter(
                Q(owner=self.request.user) | Q(members=self.request.user)
            )
            .select_related('owner')
            .prefetch_related('members')
            .distinct()
        )

    def perform_update(self, serializer):
        board = serializer.save()
        board.members.add(board.owner)


class TaskListCreateView(generics.ListCreateAPIView):
    """List accessible tasks with optional query filters or create a task."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Task.objects.filter(
                Q(board__owner=self.request.user) | Q(board__members=self.request.user)
            )
            .select_related('board', 'board__owner', 'assignee', 'reviewer')
            .distinct()
        )
        return self._apply_filters(queryset)

    def perform_create(self, serializer):
        board = serializer.validated_data['board']
        if not is_board_member(self.request.user, board):
            raise PermissionDenied('Board access denied.')
        serializer.save()

    def _apply_filters(self, queryset):
        for field in ('board', 'status', 'priority', 'assignee', 'reviewer'):
            value = self.request.query_params.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a task belonging to an accessible board."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, RelatedBoardMemberPermission]

    def get_queryset(self):
        return (
            Task.objects.filter(
                Q(board__owner=self.request.user) | Q(board__members=self.request.user)
            )
            .select_related('board', 'board__owner', 'assignee', 'reviewer')
            .distinct()
        )


class CommentListCreateView(generics.ListCreateAPIView):
    """List accessible comments or create a comment as the request user."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Comment.objects.filter(
                Q(task__board__owner=self.request.user)
                | Q(task__board__members=self.request.user)
            )
            .select_related('task', 'task__board', 'author')
            .distinct()
        )
        task_id = self.request.query_params.get('task')
        return queryset.filter(task_id=task_id) if task_id else queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a comment on an accessible board."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, RelatedBoardMemberPermission]

    def get_queryset(self):
        return (
            Comment.objects.filter(
                Q(task__board__owner=self.request.user)
                | Q(task__board__members=self.request.user)
            )
            .select_related('task', 'task__board', 'author')
            .distinct()
        )
