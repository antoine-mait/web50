from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:auction_id>/", views.listing, name="listing"),

    path("my_listing/", views.my_listing, name="my_listing"),
    path("<str:username>/", views.my_listing, name="user_profile"),

    path("watchlist/toggle/<int:auction_id>/", views.toggle_watchlist, name="toggle_watchlist"),
    path("bid/<int:auction_id>/", views.bid, name="bid"),
    path("delete_listing/<int:auction_id>/", views.delete_listing, name="delete_listing"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)