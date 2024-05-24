from django.contrib import admin
from .models import Comment, CommentSection


@admin.register(CommentSection)
class CommentSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'active')
    search_fields = ('id', 'active')
    list_filter = ('active','created_at')
    ordering = ('id',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment_section', 'author', 'message', 'edited', 'active', 'parent', 'score', 'created_at','updated_at')
    search_fields = ('author__username', 'message', 'comment_section__id')
    list_filter = ('active', 'edited', 'created_at', 'comment_section', 'score')
    ordering = ('-author', 'author')
    fieldsets = (
        (None, {
            'fields': ('comment_section', 'author', 'message', 'attachments', 'edited', 'active', 'parent', 'score')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
