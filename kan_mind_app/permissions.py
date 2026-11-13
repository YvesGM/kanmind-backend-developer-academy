from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Board, Comment, Task


def get_related_board(obj):
    """Return the board related to a board, task, or comment instance."""
    if isinstance(obj, Board):
        return obj
    if isinstance(obj, Task):
        return obj.board
    if isinstance(obj, Comment):
        return obj.task.board
    return None


def is_board_member(user, board):
    """Return whether a user owns or belongs to a board."""
    if not user or not user.is_authenticated or board is None:
        return False
    return board.owner_id == user.id or board.members.filter(pk=user.pk).exists()


class BoardAccessPermission(BasePermission):
    """Allow members to read a board and only its owner to mutate it."""

    def has_object_permission(self, request, view, obj):
        board = get_related_board(obj)
        if request.method in SAFE_METHODS:
            return is_board_member(request.user, board)
        return board is not None and board.owner_id == request.user.id


class RelatedBoardMemberPermission(BasePermission):
    """Allow board members to access related tasks and comments."""

    def has_object_permission(self, request, view, obj):
        return is_board_member(request.user, get_related_board(obj))
