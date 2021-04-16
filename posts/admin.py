from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
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


@admin.register(Group)
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


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author',
        'text',
        'created',
    )
