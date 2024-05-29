# Create your views here.
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from flowback.comment.selectors import comment_list
from flowback.comment.services import comment_create, comment_delete, comment_update
from flowback.common.pagination import LimitOffsetPagination, get_paginated_response
from flowback.comment.serializers import CommentOutputSerializer


class CommentListAPI(APIView):
    lazy_action = comment_list

    class Pagination(LimitOffsetPagination):
        default_limit = 20
        max_limit = 100

    class FilterSerializer(serializers.Serializer):
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

    class OutputSerializer(CommentOutputSerializer):
        pass  # no changes

    def get(self, request, *args, **kwargs):
        serializer = self.FilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        comments = self.lazy_action.__func__(fetched_by=request.user,
                                             filters=serializer.validated_data,
                                             *args,
                                             **kwargs)

        return get_paginated_response(pagination_class=self.Pagination,
                                      serializer_class=self.OutputSerializer,
                                      queryset=comments,
                                      request=request,
                                      view=self)


class CommentDetailAPI(CommentListAPI):
    class OutputSerializer(CommentOutputSerializer):
        replies = CommentOutputSerializer(many=True)

    def get(self, request, *args, **kwargs):
        serializer = self.FilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        comments = self.lazy_action.__func__(fetched_by=request.user,
                                             filters=serializer.validated_data,
                                             *args,
                                             **kwargs)

        return get_paginated_response(pagination_class=self.Pagination,
                                      serializer_class=self.OutputSerializer,
                                      queryset=comments,
                                      request=request,
                                      view=self)


class CommentCreateAPI(APIView):
    lazy_action = comment_create

    class InputSerializer(serializers.Serializer):
        parent_id = serializers.IntegerField(required=False)
        message = serializers.CharField(required=False)
        attachments = serializers.ListField(child=serializers.FileField(), required=False, max_length=10)

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = self.lazy_action.__func__(*args,
                                            author_id=request.user.id,
                                            **kwargs,
                                            **serializer.validated_data)

        return Response(status=status.HTTP_200_OK, data=comment.id)


class CommentUpdateAPI(APIView):
    lazy_action = comment_update

    class InputSerializer(serializers.Serializer):
        message = serializers.CharField()

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.lazy_action.__func__(*args,
                                  **kwargs,
                                  fetched_by=request.user.id,
                                  data=serializer.validated_data)

        return Response(status=status.HTTP_200_OK)


class CommentDeleteAPI(APIView):
    lazy_action = comment_delete

    def post(self, request, *args, **kwargs):
        self.lazy_action.__func__(*args,
                                  **kwargs,
                                  fetched_by=request.user)

        return Response(status=status.HTTP_200_OK)
