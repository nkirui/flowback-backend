from rest_framework import serializers

from flowback.files.serializers import FileSerializer


class CommentListOutputSerializer(serializers.Serializer):
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


class CommentDetailOutputSerializer(CommentListOutputSerializer):
    replies = CommentListOutputSerializer(many=True)


class CommentFilterSerializer(serializers.Serializer):
    order_by = serializers.ChoiceField(choices=['created_at_asc',
                                                'created_at_desc',
                                                'total_replies_asc',
                                                'total_replies_desc',
                                                'score_asc',
                                                'score_desc'], default='created_at_desc')
    id = serializers.IntegerField(required=False)
    message__icontains = serializers.ListField(child=serializers.CharField(), required=False)
    author_id = serializers.IntegerField(required=False)
    author_id__in = serializers.CharField(required=False)
    parent_id = serializers.IntegerField(required=False)
    has_attachments = serializers.BooleanField(required=False, allow_null=True, default=None)
    score__gt = serializers.IntegerField(required=False)
    score__lt = serializers.IntegerField(required=False)


class CommentCreateInputSerializer(serializers.Serializer):
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField()
    attachments = serializers.ListField(child=serializers.FileField(), required=False, max_length=10)


class CommentUpdateInputSerializer(serializers.Serializer):
    message = serializers.CharField()
