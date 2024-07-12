"""
Posts Tests
"""
# Standard library imports.
from datetime import date

# Related third party imports.
from django.test import TestCase
from ninja.testing import TestClient

# Local application/library specific imports.
from .models import Post, Comment
from .api import api as posts_api
from authorization.api import api as authorization_api
from .utils import get_user_with_token, get_token_with_user
from authorization.models import CustomUser


def get_access_token():
    if CustomUser.objects.filter(username="test").exists():
        test_user = CustomUser.objects.get(username="test")
        if get_token_with_user(test_user.id):
            return get_token_with_user(test_user.id)

    authorization_client = TestClient(authorization_api)
    data = {
        "username": "test",
        "email": "test@test.com",
        "password": "test"
    }
    response = authorization_client.post('/register', json=data)

    # Extract the token from registration response
    token = response.json()["token"]
    return token


class PostAPITests(TestCase):

    def setUp(self):
        self.client = TestClient(posts_api)
        self.post, created = Post.objects.get_or_create(title="Test Post", content="Test Content")
        self.token = get_access_token()

    def test_create_post(self):
        data = {"title": "New Post", "content": "New Content"}
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.post('/create', json=data, headers=headers)

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, 201)

        # Assert the created post exists in the database
        created_post = Post.objects.get(title="New Post")
        self.assertEqual(response.json()["id"], created_post.id)
        self.assertEqual(response.json()["title"], created_post.title)
        self.assertEqual(response.json()["content"], created_post.content)

    def test_get_post(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/detail/" + str(self.post.id), headers=headers)

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert the response data is correct
        self.assertEqual(response.json()["id"], self.post.id)
        self.assertEqual(response.json()["title"], self.post.title)
        self.assertEqual(response.json()["content"], self.post.content)

    def test_list_posts(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get('/list', headers=headers)

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert the correct number of posts are returned
        self.assertEqual(len(response.json()), Post.objects.count())

    def test_update_post(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"title": "Updated Post", "content": "Updated Content"}
        response = self.client.put('/update/' + str(self.post.id), json=data, headers=headers)

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert the post was updated correctly
        updated_post = Post.objects.get(id=self.post.id)
        self.assertEqual(updated_post.title, "Updated Post")
        self.assertEqual(updated_post.content, "Updated Content")

    def test_delete_post(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.delete("/delete/" + str(self.post.id), headers=headers)

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert the post was deleted from the database
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=self.post.id)


class CommentAPITests(TestCase):

    def setUp(self):
        self.client = TestClient(posts_api)
        self.token = get_access_token()
        self.post, created = Post.objects.get_or_create(title="Test Post", content="Test Content")
        self.comment, created = Comment.objects.get_or_create(post=self.post, text="Test Comment",
                                                              author=get_user_with_token(self.token))

    def test_create_comment(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"text": "New Comment", "post_id": self.post.id}
        response = self.client.post("/comment/create", json=data, headers=headers)

        # Assert the response status code is 201 OK
        self.assertEqual(response.status_code, 201)

        # Assert the created comment exists in the database
        created_comment = Comment.objects.get(text="New Comment")
        self.assertEqual(response.json()["id"], created_comment.id)
        self.assertEqual(response.json()["post_id"], self.post.id)
        self.assertEqual(response.json()["text"], created_comment.text)

    def test_get_comment(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/comment/detail/" + str(self.comment.id), headers=headers)

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert the response data is correct
        self.assertEqual(response.json()["id"], self.comment.id)
        self.assertEqual(response.json()["post_id"], self.post.id)
        self.assertEqual(response.json()["text"], self.comment.text)

    def test_list_comments(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/comment/list", headers=headers)

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert the correct number of comments are returned
        self.assertEqual(len(response.json()), Comment.objects.filter(post_id=self.post.id).count())

    def test_update_comment(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"text": "Updated Comment", "post_id": self.post.id}
        response = self.client.put("/comment/update/" + str(self.comment.id), json=data, headers=headers)

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert the comment was updated correctly
        updated_comment = Comment.objects.get(id=self.comment.id)
        self.assertEqual(updated_comment.text, "Updated Comment")

    def test_delete_comment(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.delete("/comment/delete/" + str(self.comment.id), headers=headers)

        self.assertEqual(response.status_code, 200)

        # Assert the post was deleted from the database
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=self.comment.id)


class TestCommentsDailyBreakdownAPI(TestCase):

    def setUp(self):
        self.client = TestClient(posts_api)
        self.token = get_access_token()

    def test_valid_date_range(self):
        # Test with valid date range
        headers = {"Authorization": f"Bearer {self.token}"}
        date_from = '2022-01-01'
        date_to = str(date.today())
        response = self.client.get(f'/comments-daily-breakdown?date_from={date_from}&date_to={date_to}', headers=headers)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check if response structure is as expected
        self.assertIsInstance(data, list)

        # Check individual day entries

        for entry in data:
            dt_created = entry['date']
            comments = Comment.objects.filter(dt_created__date=dt_created)
            comments_created = comments.count()
            comments_blocked = comments.filter(is_blocked=True)
            self.assertEqual(entry['comments_created'], comments_created)
            self.assertEqual(entry['comments_blocked'], comments_blocked)

    def test_invalid_date_format(self):
        # Test with invalid date format
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get('/comments-daily-breakdown?date_from=2022-01-01&date_to=invalid_date', headers=headers)
        self.assertEqual(response.status_code, 422)  # Assuming 400 for bad request

    def test_date_to_before_date_from(self):
        # Test with date_to before date_from
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get('/comments-daily-breakdown?date_from=2022-01-10&date_to=2022-01-05', headers=headers)
        self.assertEqual(response.status_code, 400)  # Assuming 400 for bad request
