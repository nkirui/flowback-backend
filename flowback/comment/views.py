# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from flowback.comment.selectors import comment_list
from flowback.comment.services import comment_create, comment_delete, comment_update
from flowback.common.pagination import LimitOffsetPagination, get_paginated_response
from flowback.comment.serializers import (CommentListOutputSerializer,
                                          CommentDetailOutputSerializer,
                                          CommentFilterSerializer,
                                          CommentCreateInputSerializer,
                                          CommentUpdateInputSerializer)

class CommentPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 100


class CommentListAPI(APIView):
    """
    Returns a list of comments based on the filters provided.
    """
    lazy_action = comment_list

    def get(self, request, *args, **kwargs):
        """
        Get list of comments given a comment section

        Kwargs from URL:
        - comment_section: id of the comment section

        Request query params:
        - limit: number of comments to fetch
        - offset: offset of the comments to fetch
        """
        print(args, kwargs)
        serializer = CommentFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        comments = self.lazy_action.__func__(fetched_by=request.user,
                                             filters=serializer.validated_data,
                                             *args,
                                             **kwargs)

        return get_paginated_response(pagination_class=CommentPagination,
                                      serializer_class=CommentListOutputSerializer,
                                      queryset=comments,
                                      request=request,
                                      view=self)


class CommentDetailAPI(APIView):
    """
    Returns details of a single comment based on the filters provided.
    """
    def get(self, request, *args, **kwargs):
        """
        Get details of a single comment based on the filters provided.

        Kwargs from URL:
        - comment_id: id of the comment
        - comment_section: id of the comment section

        Request query params:
        - include_descendants: include all descendants of the comment
        - include_ancestors: include all ancestors of the comment
        - limit: number of descendants/ancestors to fetch including the original comment
        - offset: offset of the descendants/ancestors to fetch including the original comment
        """
        comment = self.lazy_action.__func__(fetched_by=request.user,
                                             filters=kwargs,
                                             *args,
                                             **kwargs)

        include_descendants = request.query_params.get('include_descendants', False)
        include_ancestors = request.query_params.get('include_ancestors', False)
        if not any([include_ancestors, include_descendants]):
            return Response(data=CommentDetailOutputSerializer(comment).data)

        elif all([include_descendants, include_ancestors]):
            return Response(
                data={"message": "Can only request one of `include_descendants` or `include_descendants` and not both."},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            if include_descendants:
                replies = comment.descendants(include_self=True)
            elif include_ancestors:
                replies = comment.ancestors(include_self=True).extra(order_by=["-created_at"])
                # change the ordering so that the results does not cut out the comment we are fetching ancestors for
            return get_paginated_response(pagination_class=CommentPagination,
                                      serializer_class=CommentListOutputSerializer,
                                      queryset=replies,
                                      request=request,
                                      view=self)

class CommentCreateAPI(APIView):
    """Creates a new comment."""
    lazy_action = comment_create

    def post(self, request, *args, **kwargs):
        """
        Create a new comment based on the data provided.

        Kwargs from URL:
        - comment_section: id of the comment section

        Request data:
        - parent_id: id of the parent comment (if any)
        - message: message of the comment
        - attachments: list of attachments

        """
        serializer = CommentCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = self.lazy_action.__func__(*args,
                                            author_id=request.user.id,
                                            **kwargs,
                                            **serializer.validated_data)

        return Response(status=status.HTTP_200_OK, data=comment.id)


class CommentUpdateAPI(APIView):
    """Updates an existing comment."""
    lazy_action = comment_update

    def post(self, request, *args, **kwargs):
        """
        Update an existing comment based on the data provided.

        Kwargs from URL:
        - comment_id: id of the comment
        - comment_section: id of the comment section

        Request data:
        - message: message of the comment
        """
        serializer = CommentUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.lazy_action.__func__(*args,
                                  **kwargs,
                                  fetched_by=request.user.id,
                                  data=serializer.validated_data)

        return Response(status=status.HTTP_200_OK)


class CommentDeleteAPI(APIView):
    """Deletes an existing comment."""
    lazy_action = comment_delete

    def post(self, request, *args, **kwargs):
        """
        Delete an existing comment.

        Kwargs from URL:
        - comment_id: id of the comment
        - comment_section: id of the comment section
        """
        self.lazy_action.__func__(*args,
                                  **kwargs,
                                  fetched_by=request.user)

        return Response(status=status.HTTP_200_OK)
