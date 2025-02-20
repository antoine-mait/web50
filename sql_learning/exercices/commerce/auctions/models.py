from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORY_CHOICES = [
    ('fashion', 'Fashion'),
    ('toys', 'Toys'),
    ('electronics', 'Electronics'),
    ('home', 'Home'),
    ('other', 'Other'),
]
class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, null=True, choices=CATEGORY_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name="auctions", null=True)
    is_active = models.BooleanField(default=True)  
    closed = models.BooleanField(default=False) 
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

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
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.user.username} on {self.auction.title} - {self.amount}"