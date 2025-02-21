from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from decimal import Decimal
from .models import User, Auction, Watchlist, Bids

def render_page(request, template, **context):
    return render(request, template, {"MEDIA_URL": settings.MEDIA_URL, **context})

def index(request):
    listings = Auction.objects.all()
    watchlist_items = set()

    if request.user.is_authenticated:
        watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
        watchlist_items = set(watchlist.listings.values_list("id", flat=True))

    return render(request, "auctions/product_page.html", {
        "listings": listings,
        "MEDIA_URL": settings.MEDIA_URL,
        "watchlist_items": watchlist_items,  
        "show_watchlist_button": request.user.is_authenticated  
    })

def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user:
            login(request, user)
            return redirect("index")
        return render_page(request, "auctions/login.html", message="Invalid username and/or password.")
    return render_page(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return redirect("index")

def register(request):
    if request.method == "POST":
        if request.POST["password"] != request.POST["confirmation"]:
            return render_page(request, "auctions/register.html", message="Passwords must match.")
        try:
            user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
            user.save()
            login(request, user)
            return redirect("index")
        except IntegrityError:
            return render_page(request, "auctions/register.html", message="Username already taken.")
    return render_page(request, "auctions/register.html")

def create_listing(request):
    if request.method == "POST":
        Auction.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            price=Decimal(request.POST.get("price")),
            image_url=request.POST.get("image_url", ""),
            category=request.POST.get("category"),
            user=request.user
        )
        return redirect("index")
    return render_page(request, "auctions/create_listing.html")

def listing(request, auction_id):
    listing = get_object_or_404(Auction, id=auction_id)
    closed = listing.closed
    watchlist_items = set()

    if request.user.is_authenticated:
        watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
        watchlist_items = set(watchlist.listings.values_list("id", flat=True))

    is_in_watchlist = listing.id in watchlist_items if request.user.is_authenticated else False
    show_watchlist_button = request.user.is_authenticated  # Afficher le bouton seulement si l'utilisateur est connecté

    return render(request, "auctions/product_page.html", {
        "listings": [listing],
        "MEDIA_URL": settings.MEDIA_URL,
        "is_in_watchlist": is_in_watchlist,
        "watchlist_items": watchlist_items,
        "closed": closed,
        "show_watchlist_button": show_watchlist_button
    })

def watchlist(request):
    watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
    listings = watchlist.listings.all()
    
    return render(request, "auctions/product_page.html", {
        "listings": listings,
        "MEDIA_URL": settings.MEDIA_URL,
        "watchlist_items": set(listings.values_list("id", flat=True)),
        "show_watchlist_button": True 
    })

def toggle_watchlist(request, auction_id):
    if request.user.is_authenticated:
        listing = get_object_or_404(Auction, id=auction_id)
        watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
        if listing in watchlist.listings.all():
            watchlist.listings.remove(listing)
        else:
            watchlist.listings.add(listing)
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    return redirect("login")

def bid(request, auction_id):
    if not request.user.is_authenticated:
        return redirect("login")
    listing = get_object_or_404(Auction, id=auction_id)
    try:
        user_bid = Decimal(request.POST.get("amount", ""))
        if user_bid > listing.price:
            Bids.objects.create(amount=user_bid, auction=listing, user=request.user)
            listing.price, listing.bidder = user_bid, request.user
            listing.save()
            return redirect(request.META.get("HTTP_REFERER"))
    except (ValueError, TypeError):
        pass
    return render_page(request, "auctions/product_page.html", page=listing, message_bid="Invalid bid or bid too low.")

def my_listing(request, username=None):
    user = get_object_or_404(User, username=username) if username else request.user
    if not request.user.is_authenticated:
        return redirect("login")
    listings = Auction.objects.filter(user=user)
    if user == request.user:
        title = "My Listing"
    else:
        title = f"{user.username}'s Listings"
    return render_page(request, "auctions/product_page.html", 
                       page_title=title, 
                       listings=listings)

def delete_listing(request, auction_id):
    if request.user.is_authenticated:
        Auction.objects.filter(id=auction_id, user=request.user).delete()
    return redirect("my_listing")

def close_auction(request, auction_id):
    listing = get_object_or_404(Auction, id=auction_id)
    if request.user != listing.user:
        return render_page(request, "auctions/product_page.html", page=listing, message="Only the creator can close this auction.")
    listing.closed = True
    listing.save()
    highest_bid = Bids.objects.filter(auction=listing).order_by("-amount").first()
    message = f"Auction closed at {listing.price}$. {highest_bid.user.username} won!" if highest_bid else "Auction closed. No bids placed."
    return render_page(request, "auctions/product_page.html", page=listing, message=message)
