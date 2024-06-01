import json
from pprint import pprint

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate, APITransactionTestCase

from flowback.group.models import GroupUser, Group, GroupUserInvite, GroupThread
from flowback.group.tests.factories import GroupFactory, GroupUserFactory
from flowback.group.views.group import GroupListApi, GroupCreateApi
from flowback.group.views.thread import GroupThreadCommentCreateAPI, GroupThreadCommentListAPI, GroupThreadCommentUpdateAPI, GroupThreadCommentDeleteAPI
from flowback.group.views.user import GroupInviteApi, GroupJoinApi, GroupInviteAcceptApi, GroupInviteListApi
from flowback.user.models import User
from flowback.user.tests.factories import UserFactory
from flowback.comment.models import Comment


class GroupTest(APITransactionTestCase):
    reset_sequences = True

    def setUp(self):
        (self.group_one,
         self.group_two,
         self.group_three) = [GroupFactory.create(public=True) for x in range(3)]

        (self.group_user_creator_one,
         self.group_user_creator_two,
         self.group_user_creator_three) = [GroupUserFactory.create(group=group, user=group.created_by
                                                                   ) for group in [self.group_one,
                                                                                   self.group_two,
                                                                                   self.group_three]]

        self.group_no_direct = GroupFactory.create(public=True, direct_join=False)
        self.group_no_direct_user_creator = GroupUserFactory.create(group=self.group_no_direct,
                                                                    user=self.group_no_direct.created_by)

        self.group_private = GroupFactory.create(public=False)
        self.group_private_user_creator = GroupUserFactory.create(group=self.group_private,
                                                                  user=self.group_private.created_by)

        self.groupless_user = UserFactory()

    def test_group_list(self):
        factory = APIRequestFactory()
        user = self.group_user_creator_two.user
        view = GroupListApi.as_view()

        request = factory.get('', data=dict(limit=10))
        force_authenticate(request, user=user)
        response = view(request)

        data = json.loads(response.rendered_content)
        pprint(data)

    def test_group_create(self):
        factory = APIRequestFactory()
        user = self.group_user_creator_two.user
        view = GroupCreateApi.as_view()
        data = dict(name="test",
                    description="test",
                    direct_join=True)

        request = factory.post('', data=data)
        force_authenticate(request, user=user)
        response = view(request)

        data = json.loads(response.rendered_content)
        pprint(data)

    def group_invite(self, group_user: GroupUser, to: User):
        factory = APIRequestFactory()
        view = GroupInviteApi.as_view()

        request = factory.post('', data=dict(to=to.id))
        force_authenticate(request, group_user.user)
        return view(request, group=group_user.group)

    def group_join(self, user: User, group: Group):
        factory = APIRequestFactory()
        view = GroupJoinApi.as_view()

        request = factory.post('')
        force_authenticate(request, user)
        return view(request, group=group.id)

    def test_group_invite(self):
        response = self.group_invite(self.group_no_direct_user_creator, self.groupless_user)
        pprint(response.data)

    def test_group_invite_accept(self):
        self.group_invite(self.group_no_direct_user_creator, self.groupless_user)

        factory = APIRequestFactory()
        user = self.groupless_user
        view = GroupInviteAcceptApi.as_view()
        request = factory.post('')
        force_authenticate(request, user)
        view(request, group=self.group_no_direct.id)

        self.assertTrue(GroupUser.objects.filter(user_id=self.groupless_user, group=self.group_no_direct).exists())

    def test_group_invite_accept_no_invite(self):
        factory = APIRequestFactory()
        user = self.groupless_user
        view = GroupInviteAcceptApi.as_view()
        request = factory.post('')
        force_authenticate(request, user)
        view(request, group=self.group_no_direct.id)

        self.assertFalse(GroupUser.objects.filter(user_id=self.groupless_user, group=self.group_no_direct).exists())

    def test_group_request_invite(self):
        self.group_join(self.groupless_user, self.group_no_direct)
        self.assertTrue(GroupUserInvite.objects.filter(user=self.groupless_user, group=self.group_no_direct).exists())

    def test_group_request_invite_accept(self):
        self.group_join(self.groupless_user, self.group_no_direct)

        factory = APIRequestFactory()
        user = self.group_no_direct_user_creator.user
        view = GroupInviteAcceptApi.as_view()
        request = factory.post('', data=dict(to=self.groupless_user.id))
        force_authenticate(request, user)
        view(request, group=self.group_no_direct.id)

        self.assertTrue(GroupUser.objects.filter(user_id=self.groupless_user, group=self.group_no_direct).exists())

    def test_group_request_invite_accept_no_invite(self):
        factory = APIRequestFactory()
        user = self.group_no_direct_user_creator.user
        view = GroupInviteAcceptApi.as_view()
        request = factory.post('', data=dict(to=self.groupless_user.id))
        force_authenticate(request, user)
        view(request, group=self.group_no_direct.id)

        self.assertFalse(GroupUser.objects.filter(user_id=self.groupless_user, group=self.group_no_direct).exists())

    def test_user_invite_list(self):
        self.group_invite(self.group_no_direct_user_creator, self.groupless_user)
        self.group_invite(self.group_private_user_creator, self.groupless_user)

        factory = APIRequestFactory()
        user = self.groupless_user
        view = GroupInviteListApi.as_view()

        request = factory.get('', data=dict(limit=10))
        force_authenticate(request, user=user)
        response = view(request)

        pprint(response.data)

    def test_user_group_join_request_list(self):
        self.group_join(self.groupless_user, self.group_no_direct)
        self.group_join(self.groupless_user, self.group_private)

        for group_user, allowed in [(self.group_private_user_creator, False),
                                    (self.group_no_direct_user_creator, True)]:
            factory = APIRequestFactory()
            user = group_user.user
            view = GroupInviteListApi.as_view()

            request = factory.get('', data=dict(limit=10))
            force_authenticate(request, user=user)
            response = view(request, group=group_user.group)

            self.assertTrue(bool(response.data.get('results')) == allowed)


class GroupCommentTest(APITransactionTestCase):
    def setUp(self):
        self.group = GroupFactory.create(public=True)
        self.group_user = GroupUserFactory.create(group=self.group)
        self.user = self.group_user.user
        self.group_thread = GroupThread.objects.create(created_by=self.group_user)

    def test_can_add_comment_to_group_thread(self):
        view = GroupThreadCommentCreateAPI.as_view()
        data = dict(message="test", parent_id=None, attachments=[])
        factory = APIRequestFactory()
        request = factory.post("", data=data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request, thread_id=self.group_thread.id)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(GroupThread.objects.count() == 1)
        self.assertTrue(Comment.objects.count()==1)

    def test_can_list_comments_in_a_group_thread(self):
        create_view = GroupThreadCommentCreateAPI.as_view()
        factory = APIRequestFactory()
        for i in range(10):
            data = dict(message=f"test {i}", parent_id=None, attachments=[])
            request = factory.post("", data=data, format="json")
            force_authenticate(request, user=self.user)
            create_view(request, thread_id=self.group_thread.id)

        self.assertEqual(Comment.objects.count(), 10)

        fetch_view = GroupThreadCommentListAPI.as_view()
        request = factory.get("", format="json")
        force_authenticate(request, user=self.user)
        response = fetch_view(request, thread_id=self.group_thread.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.data), ["limit", "offset", "count", "next", "previous", "results"])  # check keys
        expected_messages = [f"test {i}" for i in range(10)]
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(sorted([cmt["message"] for cmt in response.data["results"]]), sorted(expected_messages))
