from django.contrib import admin

from .models import Comment, Group, Follow, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'text',
        'pub_date',
        'author',
        'group'
    )
    search_fields = (
        'text',
    )
    list_filter = (
        'pub_date',
        'group',
    )
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'description',
    )
    search_fields = (
        'text',
    )
    prepopulated_fields = {
        'slug': ('title',)
    }
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author',
        'text',
        'created'
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
