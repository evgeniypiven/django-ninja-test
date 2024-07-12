"""
Posts Celery Tasks
"""
# Standard library imports.

# Related third party imports.
from celery import shared_task

# Local application/library specific imports.
from .models import Comment, Post
from authorization.models import CustomUser


@shared_task
def auto_reply_post_comments(post_id, user_id):
    post = Post.objects.get(id=post_id)
    user = CustomUser.objects.get(id=user_id)

    comments = Comment.objects.filter(author=user, post=post)

    for comment in comments:
        reply_content = f"Thank you for your comment on '{post.title}'. We appreciate your feedback!"
        Comment.objects.create(
            parent=comment,
            post=post,
            author=user,
            text=reply_content,
        )

    post.enable_auto_reply = False
    post.save()


