from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Bids, Auction

@receiver(post_save, sender=Bids)
def update_auction_price_on_bid(sender, instance, **kwargs):
    """ Update auction price and highest bidder when a new bid is placed """
    auction = instance.auction
    highest_bid = auction.bids.order_by("-amount").first()

    if highest_bid:
        auction.price = highest_bid.amount
        auction.bidder = highest_bid.user

    auction.save()

@receiver(post_delete, sender=Bids)
def update_auction_price_on_bid_deletion(sender, instance, **kwargs):
    auction = instance.auction
    highest_bid = auction.bids.order_by("-amount").first()  # Get the next highest bid

    if highest_bid:
        auction.price = highest_bid.amount  # Restore price to highest remaining bid
        auction.bidder = highest_bid.user  # Set new highest bidder
    else:
        auction.price = auction.starting_price  # Reset to original listing price
        auction.bidder = None  # Remove active bidder if no bids remain

    auction.save()