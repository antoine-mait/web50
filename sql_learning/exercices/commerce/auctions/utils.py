from .models import Bids

def get_highest_bid(listing):
    """
    This function fetches the highest bid for a given auction listing.
    """
    return Bids.objects.filter(auction=listing).order_by("-amount").first()
