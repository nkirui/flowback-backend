from django.db import models

from flowback.common.models import BaseModel
from flowback.files.models import FileCollection
from flowback.user.models import User


class CommentSection(BaseModel):
    active = models.BooleanField(default=True)


class Comment(BaseModel):
    comment_section = models.ForeignKey(CommentSection, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=10000)
    attachments = models.ForeignKey(FileCollection, on_delete=models.SET_NULL, null=True, blank=True)
    edited = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField(default=0)

    def is_root_comment(self):
        """Check if this comment is a root comment (no parent)"""
        return self.parent is None

    def get_children(self):
        """Retrieve all direct child comments."""
        return Comment.objects.filter(parent=self)
