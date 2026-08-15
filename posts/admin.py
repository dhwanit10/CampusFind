from django.contrib import admin
from .models import UserProfile, Post, Campus, Like, Comment, Follow

@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'campus', 'bio']
    list_filter = ['campus']
    search_fields = ['user__username', 'campus__name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'caption_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'caption']
    
    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if obj.caption else '(no caption)'
    caption_preview.short_description = 'Caption'

admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follow)