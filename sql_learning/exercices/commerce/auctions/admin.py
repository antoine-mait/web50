from django.contrib import admin

# Register your models here.
from .models import User, Auction

# Register your models here.

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "price", "image_url")

admin.site.register(User)
admin.site.register(Auction, AuctionAdmin)
