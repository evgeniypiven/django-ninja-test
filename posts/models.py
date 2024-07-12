"""
Posts Models
"""
# Standard library imports.

# Related third party imports.
from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from django.utils import timezone
from better_profanity import profanity

# Local application/library specific imports.
from authorization.models import CustomUser
from .utils import LocationUploadGenerator


def location_image_upload(instance, filename):
    return LocationUploadGenerator().generate(instance, filename)


class PostManager(models.Manager):
    def only_active(self):
        return self.get_queryset().filter(is_blocked=False)


class Post(models.Model):
    title = models.CharField(
        _('Title'),
        max_length=128,
        null=True,
        blank=True,
        unique=True
    )
    content = RichTextField(
        _('Text'),
        null=True,
        blank=True
    )
    photo = models.ImageField(
        blank=True,
        upload_to=location_image_upload
    )
    dt_created = models.DateTimeField(
        _('Created At'),
        default=timezone.now,
        null=False,
        blank=False,
        help_text=_('Date and time when post was added')
    )
    dt_updated = models.DateTimeField(
        _('Updated At'),
        auto_now=True,
        null=True,
        blank=True,
        help_text=_('Date and time when post was updated')
    )

    is_blocked = models.BooleanField(
        _('Is Blocked'),
        default=False
    )

    enable_auto_reply = models.BooleanField(
        _('Enable Auto Reply'),
        default=False
    )

    objects = PostManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.is_blocked = True if profanity.contains_profanity(self.title) or \
                profanity.contains_profanity(self.content) else False
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'posts'
        db_table = 'starnavi_posts'
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')


class CommentManager(models.Manager):
    def only_active(self):
        return self.get_queryset().filter(is_blocked=False)


class Comment(models.Model):
    text = RichTextField(
        _('Text'),
        null=False,
        blank=False
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name=_('Author'),
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        verbose_name=_('Post'),
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )
    dt_created = models.DateTimeField(
        _('Created At'),
        default=timezone.now,
        null=False,
        blank=False,
        help_text=_('Date and time when post was added')
    )
    dt_updated = models.DateTimeField(
        _('Updated At'),
        auto_now=True,
        null=True,
        blank=True,
        help_text=_('Date and time when post was updated')
    )

    is_blocked = models.BooleanField(
        _('Is Blocked'),
        default=False
    )

    objects = CommentManager()

    def __str__(self):
        return f'Comment by {self.author} with id {self.pk}'

    def save(self, *args, **kwargs):
        self.is_blocked = True if profanity.contains_profanity(self.text) else False
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'posts'
        db_table = 'starnavi_comments'
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
