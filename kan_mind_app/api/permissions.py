from rest_framework.permissions import BasePermission, SAFE_METHODS

from ..models import Board, Comment, Task


def is_board_member(user, board):
    """Return whether the user owns or belongs to the board."""
    if not user or not user.is_authenticated:
        return False
    return board.owner_id == user.id or board.members.filter(pk=user.pk).exists()


class BoardPermission(BasePermission):
    """Apply the board permission matrix from the API contract."""

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return obj.owner_id == request.user.id
        return is_board_member(request.user, obj)


class TaskPermission(BasePermission):
    """Allow board members to edit tasks and creators/owners to delete them."""

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return self._can_delete(request.user, obj)
        if request.method in SAFE_METHODS:
            return is_board_member(request.user, obj.board)
        return is_board_member(request.user, obj.board)

    @staticmethod
    def _can_delete(user, task):
        return task.creator_id == user.id or task.board.owner_id == user.id


class IsCommentAuthor(BasePermission):
    """Allow deletion only by the comment author."""

    def has_object_permission(self, request, view, obj):
        return obj.author_id == request.user.id
