from django.contrib import admin
from .models import User, Auction, Bids

# Register User model
admin.site.register(User)

# Custom inline admin for Bids inside Auction panel
class BidsInline(admin.TabularInline):
    model = Bids
    extra = 0  # Prevents empty bid slots

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "price", "current_highest_bid", "closed")  # Fixed field names
    inlines = [BidsInline]  # Show related bids in the Auction panel
    actions = ["delete_last_bid"]  # Custom action to remove the last bid

    def current_highest_bid(self, obj):
        last_bid = obj.bids.order_by("-timestamp").first()  # Get latest bid
        return last_bid.amount if last_bid else "No bids"

    @admin.action(description="Delete last bid for selected auctions")
    def delete_last_bid(self, request, queryset):
        for auction in queryset:
            last_bid = auction.bids.order_by("-timestamp").first()
            if last_bid:
                last_bid.delete()
                self.message_user(request, f"Deleted last bid on {auction.title}.")

admin.site.register(Auction, AuctionAdmin)
