from django.contrib import admin
from .models import Post, Like

def reset_likes(modeladmin, request, queryset):
    for post in queryset:
        post.count_likes = 0
        post.save()
        Like.objects.filter(like=post).delete()

reset_likes.short_description = "Reset likes for selected posts"

class PostAdmin(admin.ModelAdmin):
    actions = [reset_likes]

admin.site.register(Post, PostAdmin)