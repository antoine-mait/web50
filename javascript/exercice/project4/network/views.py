from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

from .models import User , Post , Follow , Comment , Like


def index(request):
    posts = Post.objects.all().order_by('-post_time')
    like_items = set()
    count_likes = 0


    if request.user.is_authenticated:
        # Get the list of post IDs that the user has liked
        like_items = set(Like.objects.filter(user=request.user).values_list("like_id", flat=True))

    count_likes = len(like_items)
    print(count_likes)

    return render(request, "network/index.html", {
        "posts": posts,
        "MEDIA_URL": settings.MEDIA_URL,
        "like_items": like_items,  
        "count_likes" : count_likes,
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
    likes = post.likes
    comments = Comment.objects.filter(post=post)

    if request.user.is_authenticated:
        like_items = set(Like.objects.filter(user=request.user).values_list("like_id", flat=True))
        print(f"User {request.user.username} liked posts: {like_items}")
    else:
        like_items = set()


    is_in_liked = post.id in like_items if request.user.is_authenticated else False
    show_like_button = request.user.is_authenticated  # Afficher le bouton seulement si l'utilisateur est connecté
    
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
        
        return redirect('post', post_id=post_id)
    
    return render(request, "network/index.html", {
        "posts": [post],
        "post_id": post,
        "likes" : likes,
        "is_in_liked": is_in_liked,
        "like_items": like_items,
        "show_like_button": show_like_button,
        "comments" : comments,
    })

def toggle_like(request, post_id):

    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        like = Like.objects.filter(user=request.user, like=post).first()
        
        if like:
            post.count_likes -= 1
            like.delete()  # Unlike
        else:
            post.count_likes += 1
            Like.objects.create(user=request.user, like=post)  # Like
        
        post.save()

        return redirect(request.META.get('HTTP_REFERER', 'index'))
    
    return redirect("login")
