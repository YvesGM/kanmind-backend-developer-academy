from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Board, Comment, Task
from .permissions import (
    BoardPermission,
    IsCommentAuthor,
    TaskPermission,
    is_board_member,
)
from .serializers import (
    AuthResponseSerializer,
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateResponseSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    LoginSerializer,
    RegistrationSerializer,
    TaskDashboardSerializer,
    TaskUpdateResponseSerializer,
    TaskWriteSerializer,
    UserSummarySerializer,
    user_fullname,
)

User = get_user_model()


def auth_payload(user, token):
    """Build the authentication response required by the frontend."""
    return {
        'token': token.key,
        'fullname': user_fullname(user),
        'email': user.email,
        'user_id': user.id,
    }


def accessible_boards(user):
    """Return boards visible to the authenticated user."""
    return Board.objects.filter(
        Q(owner=user) | Q(members=user)
    ).distinct()


def board_list_queryset(user):
    """Return accessible boards with dashboard counts."""
    return accessible_boards(user).annotate(
        member_count=Count('members', distinct=True),
        ticket_count=Count('tasks', distinct=True),
        tasks_to_do_count=Count(
            'tasks', filter=Q(tasks__status=Task.Status.TODO), distinct=True
        ),
        tasks_high_prio_count=Count(
            'tasks', filter=Q(tasks__priority=Task.Priority.HIGH), distinct=True
        ),
    )


def task_queryset():
    """Return tasks optimized for API serialization."""
    return Task.objects.select_related(
        'board', 'board__owner', 'assignee', 'reviewer', 'creator'
    ).annotate(comments_count=Count('comments'))


class RegistrationView(APIView):
    """Register a user and return an authentication token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        payload = auth_payload(user, token)
        return Response(
            AuthResponseSerializer(payload).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate a user and return the existing or new token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response(AuthResponseSerializer(auth_payload(user, token)).data)


class EmailCheckView(APIView):
    """Return the matching user for an authenticated email lookup."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email', '').strip()
        if not email:
            return Response(
                {'email': ['This query parameter is required.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = get_object_or_404(User, email__iexact=email)
        return Response(UserSummarySerializer(user).data)


class BoardViewSet(viewsets.ModelViewSet):
    """Handle board CRUD according to the KanMind contract."""

    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, BoardPermission]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        if self.action == 'list':
            return board_list_queryset(self.request.user)
        tasks = task_queryset().order_by('id')
        return Board.objects.select_related('owner').prefetch_related(
            'members',
            Prefetch('tasks', queryset=tasks),
        )

    def get_serializer_class(self):
        serializers = {
            'list': BoardListSerializer,
            'create': BoardCreateSerializer,
            'retrieve': BoardDetailSerializer,
            'partial_update': BoardUpdateSerializer,
        }
        return serializers.get(self.action, BoardDetailSerializer)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=request.user)
        board = board_list_queryset(request.user).get(pk=board.pk)
        data = BoardListSerializer(board).data
        return Response(data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        board = self.get_object()
        serializer = self.get_serializer(board, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        data = BoardUpdateResponseSerializer(board).data
        return Response(data)


class TaskViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Handle task creation, updates, deletion, and dashboard actions."""

    queryset = Task.objects.all()
    serializer_class = TaskWriteSerializer
    permission_classes = [IsAuthenticated, TaskPermission]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return task_queryset()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        task = task_queryset().get(pk=serializer.instance.pk)
        data = TaskDashboardSerializer(task).data
        return Response(data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskUpdateResponseSerializer(task).data)

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        tasks = task_queryset().filter(assignee=request.user)
        return Response(TaskDashboardSerializer(tasks, many=True).data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        tasks = task_queryset().filter(reviewer=request.user)
        return Response(TaskDashboardSerializer(tasks, many=True).data)


class TaskCommentsView(generics.ListCreateAPIView):
    """List or create comments nested below a task."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_task(self):
        task = get_object_or_404(
            Task.objects.select_related('board'),
            pk=self.kwargs['task_id'],
        )
        if not is_board_member(self.request.user, task.board):
            raise PermissionDenied('Board membership required.')
        return task

    def get_queryset(self):
        task = self.get_task()
        return Comment.objects.filter(task=task).select_related(
            'author'
        ).order_by('created_at', 'id')

    def perform_create(self, serializer):
        serializer.save(task=self.get_task(), author=self.request.user)


class TaskCommentDeleteView(generics.DestroyAPIView):
    """Delete a nested comment when the requester is its author."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        return Comment.objects.filter(
            task_id=self.kwargs['task_id']
        ).select_related('author')
