from django.contrib import admin
from .models import MessageChannel, MessageChannelParticipant

@admin.register(MessageChannel)
class MessageChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'origin_name', 'title')


@admin.register(MessageChannelParticipant)
class MessageChannelParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'channel', 'closed_at', 'timestamp', 'active')
