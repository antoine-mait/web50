from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from .models import User , Post , Follow ,Like
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    posts = Post.objects.all().order_by('-post_time')

     # Pagination logic
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get likes information
    like_items, count_likes = get_user_likes(request)

    return render(request, "network/index.html", {
        "posts": page_obj,
        "MEDIA_URL": settings.MEDIA_URL,
        "like_items": like_items,  
        "count_likes": count_likes,
        "page_obj": page_obj,
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def create_post(request):

    if not request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "POST":  # Store user's price input

        Post.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            user=request.user
        )
        return redirect("index")

    return redirect("index")

def post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    show_like_button = request.user.is_authenticated  # Afficher le bouton seulement si l'utilisateur est connecté
    
    return render(request, "network/index.html", {
        "posts": [post],
        "post_id": post,
        "show_like_button": show_like_button,
    })

def toggle_like(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        like = Like.objects.filter(user=request.user, like=post).first()
        
        if like:
            post.count_likes -= 1
            like.delete()  # Unlike
            liked = False
        else:
            post.count_likes += 1
            Like.objects.create(user=request.user, like=post)  # Like
            liked = True
        
        post.save()

        # Return JSON response with updated information
        return JsonResponse({
            "success": True,
            "count_likes": post.count_likes,
            "liked": liked,
            "media_url": settings.MEDIA_URL
        })
    
    return JsonResponse({"error": "Authentication required"}, status=401)

def get_user_likes(request):
    if request.user.is_authenticated:
        # Get the list of post IDs that the user has liked
        like_items = set(Like.objects.filter(user=request.user).values_list("like_id", flat=True))
        count_likes = len(like_items)
        return like_items, count_likes
    return set(), 0

def get_user_followers(user):

    followers = Follow.objects.filter(profile=user).count()
    return followers

def profile(request, username=None):
    viewed_profile  = get_object_or_404(User, username=username) if username else request.user
    user  = get_object_or_404(User, username=username) if username else request.user

    # Get the list of posts for the profile page
    posts = Post.objects.filter(user=user).order_by('-post_time')
    
    # Check if the current user follows the profile
    followed_account = Follow.objects.filter(user=request.user, profile=user).exists()

    # Get likes information
    like_items, count_likes = get_user_likes(request)

    count_followers =  Follow.objects.filter(profile=user).count()

    is_profile_page = username is not None
    title = f"{user.username}'s posts" if is_profile_page else "All Posts"
    
    return render(request, "network/index.html", {
        "title": title,
        "posts": posts,
        "is_profile_page": is_profile_page,
        "MEDIA_URL": settings.MEDIA_URL,
        "followed_account": followed_account,
        "like_items": like_items,  
        "count_likes": count_likes,
        "count_followers" : count_followers,
        "viewed_profile": viewed_profile,
        "profile" : user,
        "user_page" : True,
    })

def toggle_follow(request, username):
    if request.user.is_authenticated:
        profile = get_object_or_404(User, username=username)  

        if profile == request.user:
            print("You cannot follow yourself!")  # Prevent self-following
            return redirect(request.META.get('HTTP_REFERER', 'index'))

        follow_entry = Follow.objects.filter(user=request.user, profile=profile)

        if follow_entry.exists():
            follow_entry.delete()
            print(f"Unfollowed {profile.username}")
        else:
            Follow.objects.create(user=request.user, profile=profile)
            print(f"Followed {profile.username}")

        # Debugging: Check the correct follow action
        count_followers = Follow.objects.filter(profile=profile).count()
        print(f"Total Followers for {profile.username}: {count_followers}")  # Should match the viewed profile (testwo)

        return redirect(request.META.get('HTTP_REFERER', 'index'))

    return redirect("login")

def following(request, username):

    user  = get_object_or_404(User, username=username)

    if request.user.is_authenticated:

        follows = Follow.objects.filter(user=user)

        # Initialize an empty list to hold the profiles of followed users
        followed_users = []

        # Loop through the follows to extract each followed user's profile
        for follow in follows:
            followed_users.append(follow.profile)
        
        posts = Post.objects.filter(user__in=followed_users).order_by('-post_time')  # 
        like_items, count_likes = get_user_likes(request)

        return render(request, "network/index.html", {
            "title" :  f"{request.user}'s following",
            "user_page": True,
            "posts": posts,            
            "like_items": like_items,  
            "count_likes": count_likes,
            "MEDIA_URL": settings.MEDIA_URL,
        })
    
    return redirect("login")

def post_edit(request, post_id):

    if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in"}, status=401)
        
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        edit_post = Post.objects.get(pk=post_id)
        
        # Check if the user owns this post
        if request.user != edit_post.user:
            return JsonResponse({"error": "You cannot edit this post"}, status=403)
            
        data = json.loads(request.body)
        edit_post.description = data["description"]
        edit_post.save()
        return JsonResponse({
            "message": "Change successful", 
            "data": data["description"]
        })
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
