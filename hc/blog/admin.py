from django.contrib import admin

from .models import Post



class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'created_at', 'updated_at')
    list_filter = ('author', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    raw_id_fields = ('author',)


admin.site.register(Post, PostAdmin)
