from django.contrib import admin


from .models import Post, Like, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'caption_preview', 'likes_count', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'caption')
    readonly_fields = ('created_at', 'updated_at', 'likes_count')
    
    fieldsets = (
        ('Post Info', {
            'fields': ('user', 'image', 'caption')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'likes_count'),
            'classes': ('collapse',)
        }),
    )
    
    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'post__user__username')
    readonly_fields = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'text_preview', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'text')
    readonly_fields = ('created_at', 'updated_at')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment'