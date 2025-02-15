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
    path("watchlist/toggle/<int:auction_id>/", views.toggle_watchlist, name="toggle_watchlist"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)