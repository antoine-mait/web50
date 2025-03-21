from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):

    title = models.CharField(max_length=20)
    description = models.CharField(max_length=200)
    user = models.ForeignKey(User , on_delete=models.CASCADE, related_name="post", null= True )
    post_time = models.DateTimeField(auto_now_add=True)
    count_likes = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Post uploaded at {self.post_time} by {self.user} : {self.description}"

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follow = models.ManyToManyField(Post)

    def __str__(self):
        return f"Follower of {self.user.username}"
    
class Comment(models.Model):
    content = models.TextField(max_length=255)
    post_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title} : '  {self.content} '"

class Like(models.Model):
    like = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like")

    def __str__(self):
        return f"{self.user.username} Liked your post : {self.like.title}"
    
