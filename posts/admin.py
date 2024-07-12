"""
Posts admin
"""

# Standard library imports.

# Related third party imports.
from django.contrib import admin

# Local application/library specific imports.
from .models import Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'dt_created', 'is_blocked', 'dt_updated', 'enable_auto_reply'
    )
    readonly_fields = ('dt_created', )

    search_fields = ('title',)

    fieldsets = (
        (None, {
            'fields': (
                'title', 'content', 'photo', 'dt_created'
            )
        }),
    )


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'dt_created', 'is_blocked', 'dt_updated',
    )

    readonly_fields = ('dt_created',)

    search_fields = ('author__username',)

    fieldsets = (
        (None, {
            'fields': (
                'text', 'author', 'post', 'parent', 'dt_created'
            )
        }),
    )


admin.site.register(Comment, CommentAdmin)
