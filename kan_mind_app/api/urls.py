from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BoardViewSet,
    EmailCheckView,
    LoginView,
    RegistrationView,
    TaskCommentDeleteView,
    TaskCommentsView,
    TaskViewSet,
)

router = DefaultRouter()
router.register('boards', BoardViewSet, basename='board')
router.register('tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path(
        'tasks/<int:task_id>/comments/',
        TaskCommentsView.as_view(),
        name='task-comments',
    ),
    path(
        'tasks/<int:task_id>/comments/<int:pk>/',
        TaskCommentDeleteView.as_view(),
        name='task-comment-delete',
    ),
    path('', include(router.urls)),
]
