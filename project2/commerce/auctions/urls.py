from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("close_listing/<int:listing_id>", views.close_listing, name="close_listing"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("post_comment/<int:listing_id>", views.post_comment, name="post_comment"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category_enum>", views.category, name="category"),
]
