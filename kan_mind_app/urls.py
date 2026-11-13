from django.urls import path

from . import views


urlpatterns = [
    path(
        'boards/',
        views.board_list_create,
        name='board-list-create'
    ),
    path(
        'boards/<int:pk>/',
        views.board_detail,
        name='board-detail'
    ),

    path(
        'tasks/',
        views.task_list_create,
        name='task-list-create'
    ),
    path(
        'tasks/<int:pk>/',
        views.task_detail,
        name='task-detail'
    ),

    path(
        'comments/',
        views.comment_list_create,
        name='comment-list-create'
    ),
    path(
        'comments/<int:pk>/',
        views.comment_detail,
        name='comment-detail'
    ),
]