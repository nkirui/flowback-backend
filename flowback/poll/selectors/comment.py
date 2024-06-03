from flowback.comment.selectors import comment_list, comment_detail
from flowback.common.services import get_object
from flowback.poll.models import Poll, PollDelegateVoting
from flowback.user.models import User
from flowback.group.selectors import group_user_permissions


def poll_comment_list(*, fetched_by: User, poll_id: int, filters=None):
    filters = filters or {}

    poll = get_object(Poll, id=poll_id)
    group_user_permissions(group=poll.created_by.group.id, user=fetched_by)

    return comment_list(fetched_by=fetched_by, comment_section_id=poll.comment_section.id, filters=filters)


def poll_comment_detail(*, fetched_by: User, poll_id: int, comment_id: int, filters=None):
    poll = get_object(Poll, id=poll_id)
    return comment_detail(fetched_by=fetched_by, comment_section_id=poll.comment_section.id, comment_id=comment_id)
