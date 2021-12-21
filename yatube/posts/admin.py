from django.contrib import admin

from yatube.settings import STRING_EMPTY

from .models import Comment, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = STRING_EMPTY


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    list_filter = ('title',)


@admin.register(Comment)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'pub_date')
