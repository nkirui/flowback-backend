import json
from pprint import pprint

from rest_framework.test import APIRequestFactory, force_authenticate, APITransactionTestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from flowback.comment.models import Comment
from .factories import PollFactory
from ...comment.tests.factories import CommentFactory
from ...files.models import FileSegment
from ...files.tests.factories import FileCollectionFactory, FileSegmentFactory
from ...poll.views.comment import PollCommentCreateAPI, PollCommentListAPI, PollCommentDetailAPI


class PollCommentTest(APITransactionTestCase):

    def setUp(self):
        self.collection = FileCollectionFactory()
        (self.file_one,
         self.file_two,
         self.file_three) = [FileSegmentFactory(collection=self.collection) for x in range(3)]

        self.poll = PollFactory()
        (self.poll_comment_one,
         self.poll_comment_two,
         self.poll_comment_three) = [CommentFactory(comment_section=self.poll.comment_section,
                                                    attachments=(self.collection if x == 2 else None)
                                                    ) for x in range(3)]

    def test_poll_comment_create_no_attachments(self):
        factory = APIRequestFactory()
        view = PollCommentCreateAPI.as_view()
        data = dict(message='hello')

        request = factory.post('', data=data)
        force_authenticate(request, user=self.poll.created_by.user)
        response = view(request, poll_id=self.poll.id)

        comment_id = int(json.loads(response.rendered_content))
        comment = Comment.objects.get(id=comment_id)
        self.assertEqual(comment.attachments, None)

    def test_poll_comment_create_with_attachments(self):
        factory = APIRequestFactory()
        view = PollCommentCreateAPI.as_view()

        # request without image
        data = dict(message='hello',
                    attachments=[SimpleUploadedFile('test.txt', b'test message'),
                                 SimpleUploadedFile('test.txt', b'another test message')])

        request = factory.post('', data=data)
        force_authenticate(request, user=self.poll.created_by.user)
        response = view(request, poll_id=self.poll.id)

        comment_id = int(json.loads(response.rendered_content))
        comment = Comment.objects.get(id=comment_id)
        files = comment.attachments.filesegment_set

        data_ex = dict(message='hello_2',
                       attachments=[SimpleUploadedFile('test.txt', b'test message'),
                                    SimpleUploadedFile('test.txt', b'another test message')])

        request_ex = factory.post('', data=data_ex)
        force_authenticate(request_ex, user=self.poll.created_by.user)
        response_ex = view(request_ex, poll_id=self.poll.id)

        comment_id_ex = int(json.loads(response_ex.rendered_content))
        comment_ex = Comment.objects.get(id=comment_id_ex)
        files_ex = comment_ex.attachments.filesegment_set

        self.assertEqual(all('test' not in x.file for x in files.all()), True)
        self.assertEqual(all('test' not in x.file for x in files_ex.all()), True)
        self.assertEqual(files.count(), len(data['attachments']))

        return comment_id_ex

    def test_poll_comment_list(self):
        factory = APIRequestFactory()
        view = PollCommentListAPI.as_view()

        target = self.test_poll_comment_create_with_attachments()

        request = factory.get('')
        force_authenticate(request, user=self.poll.created_by.user)
        response = view(request, poll_id=self.poll.id)

        self.assertEqual(response.status_code, 200)
        pprint([i['attachments'] for i in response.data['results'] if i['id'] == target])
        self.assertEqual(len([i['attachments'] for i in response.data['results'] if i['id'] == target][0]), 2)


    def test_fetch_poll_comment_details(self):
        factory = APIRequestFactory()
        view = PollCommentDetailAPI.as_view()
        request = factory.get('')
        force_authenticate(request, user=self.poll.created_by.user)
        response = view(request, poll_id=self.poll.id, comment_id=self.poll_comment_one.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.data.keys()), ['id','author_id', 'author_name', 'author_profile_image',
            'parent_id', 'created_at', 'edited', 'active', 'message','attachments', 'score', 'num_replies', 'replies'])

    def test_fetch_poll_comment_details_with_descendants(self):
        factory = APIRequestFactory()
        data = {"message": "test", "parent_id": self.poll_comment_one.id}
        create_view = PollCommentCreateAPI.as_view()
        request = factory.post("", data=data)
        force_authenticate(request, user=self.poll.created_by.user)
        create_response = create_view(request, poll_id=self.poll.id)

        view = PollCommentDetailAPI.as_view()
        request = factory.get('', data={"include_descendants": True})
        force_authenticate(request, user=self.poll.created_by.user)
        response = view(request, poll_id=self.poll.id, comment_id=self.poll_comment_one.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.data.keys()), ['limit', 'offset','count','next','previous','results'])
        self.assertEqual([cmt['id'] for cmt in response.data['results']], [self.poll_comment_one.id, create_response.data])

    def test_fetch_poll_comment_details_with_ancestors(self):
        factory = APIRequestFactory()
        data = {"message": "test", "parent_id": self.poll_comment_one.id}
        create_view = PollCommentCreateAPI.as_view()
        request = factory.post("", data=data)
        force_authenticate(request, user=self.poll.created_by.user)
        create_response = create_view(request, poll_id=self.poll.id)

        view = PollCommentDetailAPI.as_view()
        request = factory.get('', data={"include_ancestors": True})
        force_authenticate(request, user=self.poll.created_by.user)
        response = view(request, poll_id=self.poll.id, comment_id=create_response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.data.keys()), ['limit', 'offset','count','next','previous','results'])
        self.assertEqual([cmt['id'] for cmt in response.data['results']], [create_response.data, self.poll_comment_one.id])
