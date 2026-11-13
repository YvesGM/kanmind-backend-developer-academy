from django.urls import path

from .views import (
    BoardDetailView,
    BoardListCreateView,
    CommentDetailView,
    CommentListCreateView,
    EmailCheckView,
    LoginView,
    LogoutView,
    RegistrationView,
    TaskDetailView,
    TaskListCreateView,
)


urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
