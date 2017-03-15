from django.contrib import admin

from .models import Post, Comment



class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'created_at', 'updated_at')
    list_filter = ('author', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    raw_id_fields = ('author',)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('body', 'created_at', 'modified_at')
    list_filter = ('created_at', 'modified_at')
    search_fields = ('body',)


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
