from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from .utils import get_highest_bid , get_bidder
from django.urls import reverse
from django.contrib import messages
from decimal import Decimal
from .models import User, Auction, Watchlist, Bids , WonAuction , Comment

def render_page(request, template, **context):
    return render(request, template, {"MEDIA_URL": settings.MEDIA_URL, **context})

def index(request, category=None):
    if category:
        listings = Auction.objects.filter(category=category)  # Filter listings by category
    else:
        listings = Auction.objects.all()  # Show all listings if no category is specified

    watchlist_items = set()

    if request.user.is_authenticated:
        watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
        watchlist_items = set(watchlist.listings.values_list("id", flat=True))

        won_auction_ids = request.session.get("won_auction_ids", set())
        new_wins = []

        won_auctions = WonAuction.objects.filter(user=request.user, auction__id__in=won_auction_ids)

        for listing in listings:
            listing.highest_bid = get_highest_bid(listing)
            listing.bidder = get_bidder(listing)

            # If user is the highest bidder and the auction is closed
            if listing.bidder == request.user and listing.closed:
                if listing.id not in won_auction_ids:  # New win
                    new_wins.append(listing.id)
                    WonAuction.objects.create(user=request.user, auction=listing) 

        if new_wins:
            for win_id in new_wins:
                listing = Auction.objects.get(id=win_id)
                messages.success(request, f"You won the auction for {listing.title}!")

            # Update session with new wins
            won_auction_ids.update(new_wins)
            request.session["won_auction_ids"] = list(won_auction_ids)

        
    return render(request, "auctions/product_page.html", {
        "listings": listings,
        "MEDIA_URL": settings.MEDIA_URL,
        "watchlist_items": watchlist_items,  
        "show_watchlist_button": request.user.is_authenticated,
    })

def login_view(request):
    if request.method == "POST":
        # Handle login logic
        user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            request.session["seen_win_message"] = False

            return redirect("index")  # Redirect to the homepage or any page
    return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    request.session.pop("won_auction_ids", None)
    request.session.pop("seen_win_message", None)  # Clear seen message state
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
        price = Decimal(request.POST.get("price"))  # Store user's price input

        Auction.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            price=price,  # Set initial price
            starting_price=price,  # Save starting price separately
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
    comments = Comment.objects.filter(post=listing)

    if request.user.is_authenticated:
        watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
        watchlist_items = set(watchlist.listings.values_list("id", flat=True))

    is_in_watchlist = listing.id in watchlist_items if request.user.is_authenticated else False
    show_watchlist_button = request.user.is_authenticated  # Afficher le bouton seulement si l'utilisateur est connecté
    
    listing.highest_bid = get_highest_bid(listing)

    minimum_bid = listing.price + Decimal("0.01")

    if request.method == 'POST' and 'comment_id' in request.POST:
        comment_id = request.POST['comment_id']
        comment = get_object_or_404(Comment, id=comment_id)

        # Ensure the user is the one who posted the comment
        if comment.user == request.user:
            new_content = request.POST.get('comment')
            if new_content:
                comment.content = new_content
                comment.save()
                messages.success(request, "Your comment has been updated.")
            else:
                messages.error(request, "Please enter a valid comment.")
        
        return redirect('listing', auction_id=auction_id)
    
    return render(request, "auctions/product_page.html", {
        "listings": [listing],
        "listing_id": listing,
        "MEDIA_URL": settings.MEDIA_URL,
        "is_in_watchlist": is_in_watchlist,
        "watchlist_items": watchlist_items,
        "closed": closed,
        "show_watchlist_button": show_watchlist_button,
        "comments" : comments,
        "minimum_bid":minimum_bid,
    })      

def watchlist(request):
    watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
    listings = watchlist.listings.all()
    if not request.user.is_authenticated:
        return redirect("login")
    
    # Fetch highest bid for each listing
    for listing in listings:
            listing.highest_bid = get_highest_bid(listing)
            listing.bidder = get_bidder(listing)  # Now this returns a User object
            print(f"Listing: {listing.title}, Highest Bid: {listing.highest_bid}, Bidder: {listing.bidder}")


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

        if user_bid <= listing.price:
            return render_page(request, "auctions/product_page.html", 
                               page=listing,
                               message_bid="Bid must be strictly higher than the current price.")
        
        
        Bids.objects.create(amount=user_bid, auction=listing, user=request.user)
        listing.price, listing.bidder = user_bid, request.user
        listing.save()

        return redirect('listing', auction_id=auction_id)

    except (ValueError, TypeError):
        pass
    return render_page(request, "auctions/product_page.html", page=listing,
                        message_bid="Invalid bid or bid too low.")

def my_listing(request, username=None):
    user = get_object_or_404(User, username=username) if username else request.user

    if not request.user.is_authenticated:
        return redirect("login")
    
    listings = Auction.objects.filter(user=user)
    
    if user == request.user:
        title = "My Listing"
    else:
        title = f"{user.username}'s Listings"

    # Check if there is a message in the session, and pass it to the template
    auction_messages = {}

    # Fetch highest bid directly for each listing
    for listing in listings:
        
        listing.highest_bid = get_highest_bid(listing)

        message = request.session.get(f'auction_message_{listing.id}')
        if message:
            auction_messages[listing.id] = message
            # Clear the message from session after displaying it once
            del request.session[f'auction_message_{listing.id}']
        
    return render_page(request, "auctions/product_page.html", 
                    page_title=title, 
                    listings=listings, 
                    auction_messages=auction_messages,
                    )

def close_auction(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    if auction.user == request.user and not auction.closed:
        auction.closed = True
        auction.save()
        messages.success(request, "Auction has been closed successfully.")
    else:
        messages.error(request, "You are not authorized to close this auction.")
    return redirect('listing', auction_id=auction.id)

def delete_listing(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    if auction.user == request.user:
        auction.delete()
        messages.success(request, "Listing has been deleted.")
    else:
        messages.error(request, "You are not authorized to delete this listing.")
    return redirect('my_listing')

def comment(request , auction_id):

    auction = get_object_or_404(Auction, id=auction_id)

    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST": 
        comment_content = request.POST.get("comment")

        if comment_content: 
            Comment.objects.create(
                user=request.user,
                content=comment_content,
                post=auction
            )


            return redirect('listing', auction_id=auction_id)
        else:
            print("No comment content provided.")  # Debug line
    
    comments = Comment.objects.filter(post=auction)

    return render(request, "auctions/product_page.html", {
        "auction" : auction,
        "comments":comments,  
    })

def delete_comment(request , auction_id , comment_id):

    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        comment.delete()
        messages.success(request, "Comment has been deleted.")
    else:
        messages.error(request, "You are not authorized to delete this listing.")
    return redirect('listing', auction_id=auction_id)
