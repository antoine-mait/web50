from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse
from decimal import Decimal
from .models import User , Auction , Watchlist , Bids 


def index(request):
    listings = Auction.objects.all()  # Fetch all listings from the database
    watchlist_items_id = None

    if request.user.is_authenticated:
        # Fetch the user's watchlist
        watchlist = Watchlist.objects.filter(user=request.user).first()
        if watchlist:
            # Fetch the IDs of the listings in the watchlist
            watchlist_items_id = watchlist.listings.values_list('id', flat=True)

    return render(request, "auctions/index.html", {
        "listings": listings,  # Pass the listings to the template
        "MEDIA_URL": settings.MEDIA_URL,
        "watchlist_items_id": watchlist_items_id,        
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image_url = request.POST.get("image_url", "")
        category = request.POST.get("category")
        user=request.user

        auction = Auction(title=title,
                          description=description, 
                          price = Decimal(price), 
                          image_url=image_url, 
                          category = category,
                          user=user)
        auction.save()

        return redirect("index")

    return render(request, "auctions/create_listing.html")

def listing(request, auction_id):
    try:
        page = Auction.objects.get(id=auction_id)
    except Auction.DoesNotExist:
        raise Http404("Listing not found.")
    
    listing = get_object_or_404(Auction, id=auction_id)
    closed = listing.closed
    watchlist_items = set()  # Get watchlist items

    if request.user.is_authenticated:
        watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
        watchlist_items = set(watchlist.listings.values_list("id", flat=True))

    is_in_watchlist = False
    if request.user.is_authenticated and page.id in watchlist_items:
        is_in_watchlist = True

    return render(request, "auctions/listing.html", {
        "page": page, 
        "MEDIA_URL": settings.MEDIA_URL,
        "is_in_watchlist": is_in_watchlist,
        "watchlist_items": watchlist_items,
        "closed":closed
    })

def watchlist(request):

    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    listing = watchlist.listings.all()

    if request.user.is_authenticated:
        return render(request, "auctions/watchlist.html", {
            "listings" : listing ,
            "MEDIA_URL": settings.MEDIA_URL,
        })
    else: 
        return render(request, "auctions/register.html")
    
def toggle_watchlist(request, auction_id):
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect unauthenticated users to login

    listing = Auction.objects.get(id=auction_id)
    watchlist, _ = Watchlist.objects.get_or_create(user=request.user)

    if listing in watchlist.listings.all():
        watchlist.listings.remove(listing)  # Remove if it's in watchlist
    else:
        watchlist.listings.add(listing)  # Add if it's not

    watchlist.save()

    watchlist_items = watchlist.listings.values_list('id', flat=True)

    return redirect(request.META.get('HTTP_REFERER', 'index'))

def bid(request, auction_id):
    
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect unauthenticated users to login
    
    listing = get_object_or_404(Auction, id=auction_id)
    closed = listing.closed

    if listing.user == request.user:
        return render(request, "auctions/listing.html", {
            "page": listing, 
            "message_bid": "You cannot bid on your own listing.",  # Display message
            "closed": closed, 
            "MEDIA_URL": settings.MEDIA_URL
        })
    
    current_price = listing.price
    user_bid = request.POST.get("amount")

    # Validate the bid
    if not user_bid:  # If no bid is provided
        return render(request, "auctions/listing.html", {
            "page": listing,
            "message_bid": "Please enter a valid bid.",
            "closed": closed,
            "MEDIA_URL": settings.MEDIA_URL
        })

    try:
        user_bid = Decimal(user_bid)  # Convert string input to Decimal
    except ValueError:
        return render(request, "auctions/listing.html", {
            "page": listing,
            "message_bid": "Invalid bid format.",
            "closed": closed,
            "MEDIA_URL": settings.MEDIA_URL
        })

    # Check if the bid is greater than the current price
    if user_bid <= current_price:
        return render(request, "auctions/listing.html", {
            "page": listing,
            "message_bid": "Bid must be higher than the current price.",
            "closed": closed,
            "MEDIA_URL": settings.MEDIA_URL
        })

    # Save the bid
    new_bid = Bids(amount=user_bid, auction=listing, user=request.user)
    new_bid.save()

    # Update the listing price
    listing.price = user_bid
    listing.bidder = request.user
    listing.save()

    return redirect(request.META.get("HTTP_REFERER"))

def my_listing(request, username=None):
    
    if username is None:
        if not request.user.is_authenticated:
            return redirect("login")
        user = request.user
    
    else:
        user = get_object_or_404(User, username=username)

    my_listings= Auction.objects.filter(user=user)

    watchlist_items = set()
    bidder_auctions = Auction.objects.filter(bidder=user)
    
    closed_listings = my_listings.filter(closed=True) 
    
    if request.user.is_authenticated:
        watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
        watchlist_items = set(watchlist.listings.values_list("id", flat=True))


    return render(request, "auctions/my_listing.html", {
        "my_listings": my_listings,
        "user": user,
        "watchlist_items": watchlist_items,
        "MEDIA_URL": settings.MEDIA_URL,
        "bidder":bidder_auctions,
        "closed_listings":closed_listings,
    })

def delete_listing(request, auction_id):
    if not request.user.is_authenticated:
        return redirect("login")
    
    try:
        listing = Auction.objects.get(id=auction_id, user=request.user)  # Make sure it's the user's listing
        listing.delete()
    except Auction.DoesNotExist:
        # Optionally, show an error if the listing does not exist or is not owned by the user
        pass
    
    return redirect("my_listing")

def close_auction(request , auction_id):

    listing = get_object_or_404(Auction, id=auction_id)
    auction = Auction.objects.get(id=auction_id)

    if request.user != listing.user:
        return render(request, "auctions/listing.html", {
            "page": listing,
            "message": "Only the auction creator can close this listing.",
            "MEDIA_URL": settings.MEDIA_URL
        })

    highest_bid = Bids.objects.filter(auction=listing).order_by("-amount").first()

    if highest_bid:
        message = f"Auction Ended at {auction.price} $, {highest_bid.user.username} WON!"
    else:
        message = "Auction Ended. No bids were placed."

    listing.is_active = False
    listing.save()
    auction.closed = True  # Mark it as closed
    auction.save()

    return render(request, "auctions/listing.html", {
        "page": listing,
        "message": message,
        "MEDIA_URL": settings.MEDIA_URL,
        "closed":auction.closed,
    })