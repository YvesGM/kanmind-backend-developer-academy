# DJANGO
from django.contrib import admin

# OWN IMPORTS
from .models import Board, Task, Comment

admin.site.register(Board)
admin.site.register(Task)
admin.site.register(Comment)