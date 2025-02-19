from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.id} : Selling {self.title} at {self.price} , {self.description}"
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Auction)

    def __str__(self):
        return f"Watch list of {self.user.username}"

class Comment():
    print("test")

class Bids(models.Model):
    bid= models.DecimalField(max_digits=10, decimal_places=2)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


