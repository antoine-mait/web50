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
    watchlist_items = set()  # Use a set for quick lookup

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

        auction = Auction(title=title, description=description, price = Decimal(price), image_url=image_url)
        auction.save()

        return redirect("index")

    return render(request, "auctions/create_listing.html")

def listing(request, auction_id):
    try:
        page = Auction.objects.get(id=auction_id)
    except Auction.DoesNotExist:
        raise Http404("Listing not found.")
    
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
    })

def watchlist(request):

    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    listing = watchlist.listings.all()

    if request.user.is_authenticated:
        return render(request, "auctions/watchlist.html", {
            "listings" : listing ,
            "MEDIA_URL": settings.MEDIA_URL
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
    current_price = listing.price

    if request.method == "POST":
        user_bid = Decimal(request.POST["bid"])  # Get bid from form
    
        if user_bid <= current_price:
            raise Http404("Bid must be bigger than the current price")
        
    new_bid = Bids(bid=user_bid, auction=listing, user=request.user)
    new_bid.save()

    print("Received bid:", user_bid)

    return redirect(request.META.get("HTTP_REFERER", "index"))
