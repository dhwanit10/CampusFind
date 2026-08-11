from django.contrib import admin
from .models import UserProfile, Post, Campus
# Register your models here.


admin.site.register(UserProfile)
admin.site.register(Campus)
admin.site.register(Post)