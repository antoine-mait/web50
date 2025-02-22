from .models import Bids

def get_highest_bid(listing):
    """
    This function fetches the highest bid for a given auction listing.
    """
    return Bids.objects.filter(auction=listing).order_by("-amount").first()

def get_bidder(listing):
    """
    This function fetches the highest bid for a given auction listing.
    """
    highest_bid = Bids.objects.filter(auction=listing).order_by("-amount").first()  # Order by highest amount
    return highest_bid.user if highest_bid else None  # Return the user, or None if no bids