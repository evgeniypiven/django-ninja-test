"""
Posts API Urls
"""
# Standard library imports.
from typing import List
from datetime import datetime, timedelta

# Related third party imports.
from ninja import NinjaAPI, File, UploadedFile
from ninja.security import HttpBearer
from rest_framework.authtoken.models import Token
from django.db.models import Count, Q
from django.utils import timezone

# Local application/library specific imports.
from .exceptions import InvalidTokenException
from .schema import (
    PostRequestSchema,
    PostResponseSchema,
    CommentRequestSchema,
    CommentResponseSchema,
    NotFoundSchema,
    Message,
    AnalyticsSchema,
    AutoReplyConfigSchema
)
from .models import Post, Comment
from django_ninja_test.schema import Error
from .utils import get_user_with_token
from .tasks import auto_reply_post_comments


class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        if Token.objects.filter(key=token).exists():
            return token
        raise InvalidTokenException


api = NinjaAPI(urls_namespace='posts',
               version="1.0.0",
               title="Posts API",
               auth=GlobalAuth())


@api.exception_handler(InvalidTokenException)
def on_invalid_token(request, exc):
    return api.create_response(request, {"detail": "Invalid token supplied"}, status=401)


@api.post("/create", response={201: PostResponseSchema, 404: Error})
def create_post(request, post: PostRequestSchema):
    """
    Post creation method.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: title
    - type: String
    - description: title

    - name: content
    - type: String
    - description: content

    Response parameters(JSON):
    - name: id
    - type: Integer
    - description: id of post

    - name: title
    - type: String
    - description: title

    - name: content
    - type: String
    - description: content

    - name: photo
    - type: String
    - description: photo

    - name: dt_created
    - type: Datetime
    - description: date of post creation

    Response status(int):
    - 200 - success. created
    - 404 - fail. wrong parameters
    """
    # Check if title post already exist
    if Post.objects.filter(title=post.title).exists():
        return 404, {"message": "Post title already taken"}
    post = Post.objects.create(**post.dict())
    return 201, post


@api.get("/detail/{post_id}", response={200: PostResponseSchema, 400: Error, 404: NotFoundSchema})
def get_post(request, post_id: int):
    """
    Post detail method.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: post_id
    - type: Integer
    - description: post_id

    Response parameters(JSON):
    - name: id
    - type: Integer
    - description: id of post

    - name: title
    - type: String
    - description: title

    - name: content
    - type: String
    - description: content

    - name: photo
    - type: String
    - description: photo

    - name: dt_created
    - type: Datetime
    - description: date of post creation

    Response status(int):
    - 200 - success.
    - 400 - fail. post is blocked
    - 404 - fail. not found
    """
    try:
        post = Post.objects.get(pk=post_id)
        if post.is_blocked:
            return 400, {"message": "Post is blocked"}
        return 200, post
    except Post.DoesNotExist as e:
        return 404, {"message": "Could not find post"}


@api.get("/list", response=List[PostResponseSchema])
def list_posts(request):
    """
    Posts list method.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Response parameters(JSON):
    - list: list of posts

    Response status(int):
    - 200 - success.
    - 404 - fail. wrong parameters
    """
    return Post.objects.only_active()


@api.put("/update/{post_id}", response={200: PostResponseSchema, 400: Error, 404: NotFoundSchema})
def change_post(request, post_id: int, post_object: PostRequestSchema):
    """
    Post update method.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: title
    - type: String
    - description: title

    - name: content
    - type: String
    - description: content

    - name: post_id
    - type: Integer
    - description: post id

    Response parameters(JSON):
    - name: id
    - type: Integer
    - description: id of post

    - name: title
    - type: String
    - description: title

    - name: content
    - type: String
    - description: content

    - name: photo
    - type: String
    - description: photo

    - name: dt_created
    - type: Datetime
    - description: date of post creation

    Response status(int):
    - 200 - success. updated
    - 400 - fail. wrong parameters
    - 404 - fail. not found
    """
    try:
        # Check if title post already exist
        if Post.objects.filter(title=post_object.title).exists():
            return 400, {"message": "Post title already taken"}
        post = Post.objects.get(pk=post_id)
        for attribute, value in post_object.dict().items():
            setattr(post, attribute, value)
        post.save()
        return 200, post
    except Post.DoesNotExist as e:
        return 404, {"message": "Could not find post"}


@api.delete("/delete/{post_id}", response={200: Message, 404: NotFoundSchema})
def delete_post(request, post_id: int):
    """
    Post deletion method.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: post_id
    - type: Integer
    - description: post id

    Response parameters(JSON):
    - message: success or fail message

    Response status(int):
    - 200 - success. deleted
    - 404 - fail. not found
    """
    try:
        post = Post.objects.get(pk=post_id)
        post.delete()
        return 200, {"message": "Post was successfully deleted"}
    except Post.DoesNotExist as e:
        return 404, {"message": "Could not find post"}


@api.post("/upload-image/{post_id}", response={200: Message, 404: NotFoundSchema})
def post_image_upload(request, post_id: int, file: UploadedFile = File(...)):
    """
    Post image upload.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: post_id
    - type: Integer
    - description: post id

    - name: file
    - type: File
    - description: file of post image

    Response parameters(JSON):
    - message: success or fail message

    Response status(int):
    - 200 - success.
    - 404 - fail. not found
    """
    try:
        post = Post.objects.get(pk=post_id)
        post.photo.save(file.name, file, save=True)

        return 200, {"message": "Image of post was successfully added"}
    except Post.DoesNotExist as e:
        return 404, {"message": "Could not find post"}


@api.post("/comment/create", response={201: CommentResponseSchema, 404: NotFoundSchema})
def create_comment(request, comment: CommentRequestSchema):
    """
    Comment creation method.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: text
    - type: String
    - description: comment text

    - name: post_id
    - type: Integer
    - description: post id

    Response parameters(JSON):
    - name: id
    - type: Integer
    - description: id of comment

    - name: text
    - type: String
    - description: comment text

    - name: post_id
    - type: Integer
    - description: post id

    Response status(int):
    - 201 - success.
    - 404 - fail. not found
    """
    user = get_user_with_token(request.auth)
    if not user:
        return 404, {"message": "User by token doesn`t exists"}
    try:
        post = Post.objects.get(pk=comment.post_id)
        comment = Comment.objects.create(text=comment.text, post=post, author=user)
    except Post.DoesNotExist as e:
        return 404, {"message": "Could not find post"}

    return 201, comment


@api.get("comment/detail/{comment_id}", response={200: CommentResponseSchema, 400: Error, 404: NotFoundSchema})
def get_comment(request, comment_id: int):
    """
    Get comment detail.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: comment_id
    - type: Integer
    - description: comment id

    Response parameters(JSON):
    - name: id
    - type: Integer
    - description: id of comment

    - name: text
    - type: String
    - description: comment text

    - name: post_id
    - type: Integer
    - description: post id

    Response status(int):
    - 200 - success.
    - 400 - fail. comment is blocked
    - 404 - fail. not found
    """
    try:
        comment = Comment.objects.get(pk=comment_id)
        if comment.is_blocked:
            return 400, {"message": "Comment is blocked"}
        return 200, comment
    except Comment.DoesNotExist as e:
        return 404, {"message": "Could not find comment"}


@api.get("comment/list", response=List[CommentResponseSchema])
def list_comments(request):
    """
    Comments list method.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Response parameters(JSON):
    - list: list of comments

    Response status(int):
    - 200 - success.
    """
    return Comment.objects.only_active()


@api.put("comment/update/{comment_id}", response={200: CommentResponseSchema, 404: NotFoundSchema})
def change_comment(request, comment_id: int, comment: CommentRequestSchema):
    """
    Get comment detail.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: comment_id
    - type: Integer
    - description: comment id

    - name: text
    - type: String
    - description: comment text

    - name: post_id
    - type: Integer
    - description: post id

    Response parameters(JSON):
    - name: id
    - type: Integer
    - description: id of comment

    - name: text
    - type: String
    - description: comment text

    - name: post_id
    - type: Integer
    - description: post id

    Response status(int):
    - 200 - success. updated
    - 404 - fail. not found
    """
    user = get_user_with_token(request.auth)
    if not user:
        return 404, {"message": "User by token doesn`t exists"}
    try:
        Post.objects.get(pk=comment.post_id)
        comment_object = Comment.objects.get(pk=comment_id)
        for attribute, value in comment.dict().items():
            setattr(comment_object, attribute, value)
        comment_object.save()
        return 200, comment_object
    except Post.DoesNotExist as e:
        return 404, {"message": "Could not find post"}
    except Comment.DoesNotExist as e:
        return 404, {"message": "Could not find comment"}


@api.delete("comment/delete/{comment_id}", response={200: Message, 404: NotFoundSchema})
def delete_comment(request, comment_id: int):
    """
    Comment deletion method.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: comment_id
    - type: Integer
    - description: comment id

    Response parameters(JSON):
    - message: success or fail message

    Response status(int):
    - 200 - success. deleted
    - 404 - fail. not found
    """
    try:
        comment = Comment.objects.get(pk=comment_id)
        comment.delete()
        return 200, {"message": "Comment was successfully deleted"}
    except Comment.DoesNotExist as e:
        return 404, {"message": "Could not find comment"}


@api.get("/comments-daily-breakdown", response={200: List[AnalyticsSchema], 400: Error})
def comments_daily_breakdown(request, date_from: datetime, date_to: datetime):
    """
    Comment daily breakdown.

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: date_from
    - type: Date
    - description: date from of comment creation

    - name: date_to
    - type: Date
    - description: date to of comment creation

    Response parameters(JSON):
    - list of analytics

    Response status(int):
    - 200 - success.
    """
    if date_to < date_from:
        return 400, {"message": "date_to has to be more than date_from"}

    analytics_data = Comment.objects.filter(
        dt_created__date__gte=date_from,
        dt_created__date__lte=date_to
    ).values('dt_created__date').annotate(
        comments_created=Count('id'),
        comments_blocked=Count('id', filter=Q(is_blocked=True))
    ).order_by('dt_created__date')

    analytics_list = []
    for entry in analytics_data:
        analytics_list.append({
            'date': entry['dt_created__date'].strftime('%Y-%m-%d'),
            'comments_created': entry['comments_created'],
            'comments_blocked': entry['comments_blocked']
        })

    return 200, analytics_list


@api.post("/enable-auto-reply/{post_id}", response={200: Message, 400: Error, 404: NotFoundSchema})
def enable_auto_reply(request, post_id: int, auto_reply_config: AutoReplyConfigSchema):
    """
    Enable auto reply on comments of specific post

    Request header(body):
    - name: Authorization
    - value: Bearer xxxxxxxxxxxxxxxxxx

    Request parameters(body):
    - name: hours
    - type: Integer
    - description: hours delay for task execution

    - name: post_id
    - type: Integer
    - description: post id

    Response parameters(JSON):
    - message: success or fail message

    Response status(int):
    - 200 - success.
    - 400 - fail. post is blocked
    - 404 - fail. not found
    """
    user = get_user_with_token(request.auth)
    if not user:
        return 404, {"message": "User by token doesn`t exists"}
    try:
        post = Post.objects.get(pk=post_id)
        if post.is_blocked:
            return 400, {"message": "Post is blocked"}
        post.enable_auto_reply = True
        post.save()

        delay_hours = auto_reply_config.hours
        reply_time = datetime.now(timezone.utc) + timedelta(hours=delay_hours)

        user_id = user.id

        auto_reply_post_comments.apply_async([post_id, user_id], eta=reply_time)

        return 200, {"message": "Auto reply of post was successfully enabled"}
    except Post.DoesNotExist as e:
        return 404, {"message": "Could not find post"}
