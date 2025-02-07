import django_filters

from flowback.common.services import get_object
from flowback.group.models import GroupUserDelegatePool
from flowback.poll.models import Poll, PollVotingTypeRanking, PollDelegateVoting, \
    PollVotingTypeForAgainst
from flowback.user.models import User
from flowback.group.selectors import group_user_permissions


class BaseDelegatePollVoteFilter(django_filters.FilterSet):
    class Meta:
        model = PollDelegateVoting
        fields = dict(poll_id=['exact'])


class BasePollVoteRankingFilter(django_filters.FilterSet):
    delegate_pool_id = django_filters.NumberFilter(field_name='author_delegate__created_by')
    delegate_user_id = django_filters.NumberFilter(
        field_name='author_delegate__created_by__groupuserdelegate__group_user__user_id')

    class Meta:
        model = PollVotingTypeRanking
        fields = dict(proposal=['exact'])


class BasePollVoteForAgainstFilter(django_filters.FilterSet):
    class Meta:
        model = PollVotingTypeForAgainst
        fields = dict(proposal=['exact'])


class BasePollDelegateVotingFilter(django_filters.FilterSet):
    class Meta:
        model = PollDelegateVoting
        fields = dict(created_by=['exact'])


def delegate_poll_vote_list(*, fetched_by: User, delegate_pool_id: int, filters=None):
    filters = filters or {}
    delegate_pool = get_object(GroupUserDelegatePool, delegate_pool_id=delegate_pool_id)
    group_user_permissions(group=delegate_pool.group.id, user=fetched_by)
    qs = PollDelegateVoting.objects.filter(poll__created_by__group=delegate_pool.group).order_by('poll__created_at')
    return BaseDelegatePollVoteFilter(filters, qs).qs


def poll_vote_list(*, fetched_by: User, poll_id: int, delegates: bool = False, filters=None):
    poll = get_object(Poll, id=poll_id)
    group_user = group_user_permissions(group=poll.created_by.group.id, user=fetched_by)

    filters = filters or {}

    # Ranking
    if poll.poll_type == Poll.PollType.RANKING:
        if delegates:
            qs = PollVotingTypeRanking.objects.filter(proposal__poll=poll,
                                                      author_delegate__isnull=False).order_by('-priority').all()
        else:
            qs = PollVotingTypeRanking.objects.filter(proposal__poll=poll,
                                                      author__created_by=group_user).order_by('-priority').all()

        return BasePollVoteRankingFilter(filters, qs).qs

    # Schedule (For Against)
    if poll.poll_type == Poll.PollType.SCHEDULE:
        if delegates:
            qs = PollVotingTypeForAgainst.objects.filter(proposal__poll=poll,
                                                         author_delegate__isnull=False).order_by('-vote').all()
        else:
            qs = PollVotingTypeForAgainst.objects.filter(proposal__poll=poll,
                                                         author__created_by=group_user).order_by('-vote').all()

        return BasePollVoteForAgainstFilter(filters, qs).qs


def poll_delegates_list(*, fetched_by: User, poll_id: int, filters=None):
    filters = filters or {}

    poll = get_object(Poll, id=poll_id)
    group_user_permissions(group=poll.created_by.group.id, user=fetched_by)

    qs = PollDelegateVoting.objects.filter(poll=poll).all()
    return BasePollDelegateVotingFilter(filters, qs).qs
