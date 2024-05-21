from flowback.comment.views import CommentListAPI, CommentCreateAPI, CommentUpdateAPI, CommentDeleteAPI, CommentReplyAPI
from flowback.group.selectors import group_delegate_pool_comment_list
from flowback.group.services import (group_delegate_pool_comment_create,
                                     group_delegate_pool_comment_update,
                                     group_delegate_pool_comment_delete,
                                     group_delegate_pool_comment_reply)


class GroupDelegatePoolCommentListAPI(CommentListAPI):
    lazy_action = group_delegate_pool_comment_list


class GroupDelegatePoolCommentCreateAPI(CommentCreateAPI):
    lazy_action = group_delegate_pool_comment_create


class GroupDelegatePoolCommentCreateAPI(CommentReplyAPI):
    lazy_action = group_delegate_pool_comment_reply


class GroupDelegatePoolCommentUpdateAPI(CommentUpdateAPI):
    lazy_action = group_delegate_pool_comment_update


class GroupDelegatePoolCommentDeleteAPI(CommentDeleteAPI):
    lazy_action = group_delegate_pool_comment_delete
