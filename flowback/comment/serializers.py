from rest_framework import serializers

from flowback.files.serializers import FileSerializer


class CommentOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author_id = serializers.IntegerField()
    author_name = serializers.CharField(source='author.username')
    author_profile_image = serializers.ImageField(source='author.profile_image')
    parent_id = serializers.IntegerField(allow_null=True)
    created_at = serializers.DateTimeField()
    edited = serializers.BooleanField()
    active = serializers.BooleanField()
    message = serializers.CharField(allow_null=True)
    attachments = FileSerializer(source="attachments.filesegment_set", many=True, allow_null=True)
    score = serializers.IntegerField()
    num_replies = serializers.IntegerField()
