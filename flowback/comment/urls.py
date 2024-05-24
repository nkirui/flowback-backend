from django.urls import path

from . import views

comment_patterns = [
    # we need have all urls to CRUD the comments
    path("<int:comment_section_id>", views.CommentListAPI.as_view(), name="comment_list"),
    path("<int:comment_section_id>/<int:comment_id>", views.CommentDetailAPI.as_view(), name="comment_detail"),
]
