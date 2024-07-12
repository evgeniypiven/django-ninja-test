"""
Posts Schema
"""
# Standard library imports.
from datetime import datetime, date
from typing import Optional

# Related third party imports.
from ninja import Schema

# Local application/library specific imports.


class PostRequestSchema(Schema):
    title: str
    content: str


class PostResponseSchema(Schema):
    id: int
    title: str
    content: str
    photo: Optional[str]
    is_blocked: bool
    dt_created: datetime


class CommentRequestSchema(Schema):
    text: str
    post_id: int


class CommentResponseSchema(Schema):
    id: int
    text: str
    post_id: int
    is_blocked: bool


class NotFoundSchema(Schema):
    message: str


class Message(Schema):
    message: str


class AnalyticsSchema(Schema):
    date: date
    comments_created: int
    comments_blocked: int


class AutoReplyConfigSchema(Schema):
    hours: int
