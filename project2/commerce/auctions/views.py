from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CreateListingForm, IssueBidForm, CreateCommentForm
from .models import AuctionListing, Bid, Comment, User, ListingCategories

from datetime import datetime


def index(request):
    if request.user.is_authenticated:
        user_listings = AuctionListing.objects.filter(user_fk=request.user)
        return render(request, "auctions/index.html", {'listings':user_listings})
    else:
        return render(request, "auctions/register.html")

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

@login_required
def create_listing(request):
    if request.method == "POST":
        f = CreateListingForm(request.POST)
        listing = f.save(commit=False)
        listing.user_fk = request.user # you can check here whether user is related any author
        listing.save()

        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "auctions/create_listing.html",
            {'form': CreateListingForm}
        )

def listing(request, listing_id):
    listing = AuctionListing.objects.filter(id=listing_id).first()
    is_user_authenticated = request.user.is_authenticated

    max_bid_if_exists = Bid.objects.filter(listing_fk=listing).order_by('-amount').first() # may return None
    max_bid = max_bid_if_exists.amount if max_bid_if_exists is not None else listing.minimum_bid

    is_user_leading_bidder = False
    if max_bid_if_exists:
        leading_bidder = max_bid_if_exists.user_fk
        is_user_leading_bidder = leading_bidder == request.user

    class IssueBidFormListingAware(IssueBidForm):
        def clean(self):
            cleaned_data = super().clean()
            bid_amount = float(self['amount'].value())
            if bid_amount <= max_bid:
                raise ValidationError(
                    f"New bid must be higher than existing highest bid: {max_bid}"
                )

    if request.user.is_authenticated:
        all_watched_listings = set([watched_listing.id for watched_listing in request.user.watched.all()])
        is_on_watchlist = listing_id in all_watched_listings
        watchlist_button_text = "Remove From Watchlist" if is_on_watchlist else "Add to Watchlist"
    else:
        is_on_watchlist = None
        watchlist_button_text = None

    is_auction_closed = listing.auction_closed_time is not None
    is_user_listing_owner = listing.user_fk == request.user

    comments = Comment.objects.select_related('user_fk').all().order_by('-created_at')
    print([c.user_fk.username for c in comments])
    print(comments)

    if request.method == "POST":
        form = IssueBidFormListingAware(request.POST)
        if form.is_valid():

            bid = form.save(commit=False)
            bid.user_fk = request.user
            bid.listing_fk = listing
            bid.save()

            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        else:
            return render(request, "auctions/listing.html",
                {
                    'form': form,
                    'is_on_watchlist': is_on_watchlist,
                    'watchlist_button_text': watchlist_button_text,
                    'is_user_authenticated': is_user_authenticated,
                    'listing': listing,
                    'max_bid': max_bid,
                    'is_auction_closed': is_auction_closed,
                    'is_user_listing_owner': is_user_listing_owner,
                    'is_user_leading_bidder': is_user_leading_bidder,
                    'comment_form': CreateCommentForm(),
                    'comments': comments,
                }
            )
    else:
        return render(request, "auctions/listing.html",
            {
                'form': IssueBidFormListingAware,
                'is_on_watchlist': is_on_watchlist,
                'watchlist_button_text': watchlist_button_text,
                'is_user_authenticated': is_user_authenticated,
                'listing': listing,
                'max_bid': max_bid,
                'is_auction_closed': is_auction_closed,
                'is_user_listing_owner': is_user_listing_owner,
                'is_user_leading_bidder': is_user_leading_bidder,
                'comment_form': CreateCommentForm(),
                'comments': comments,
            }
        )


@login_required
def watchlist(request, listing_id=None):
    if request.method == "POST":
        is_on_watchlist_flag = request.POST['is_on_watchlist_flag'].lower() == 'true'
        # listing = AuctionListing.objects.filter(id=listing_id).first()
        user_obj = request.user
        print(is_on_watchlist_flag, user_obj, listing_id)
        # if listing is in user watchlist, remove it
        if is_on_watchlist_flag:
            user_obj.watched.remove(listing_id)

        # if listing is NOT in user watchlist, add it
        else:
            user_obj.watched.add(listing_id)

        user_obj.save()
        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    else:
        all_watched = request.user.watched.all()
        return render(request, "auctions/watchlist.html", {'listings':all_watched})

def close_listing_helper(user_obj, listing_obj, closed_by_user=False):
    max_bid_if_exists = Bid.objects.filter(listing_fk=listing_obj).order_by('-amount').first() # may return None

    if max_bid_if_exists:
        max_bid_if_exists.is_winning_bid = True
        listing_obj.winning_bid = max_bid_if_exists

    listing_obj.is_closed_by_user = closed_by_user
    listing_obj.auction_closed_time = datetime.now()

    max_bid_if_exists.save()
    listing_obj.save()

@login_required
@require_POST
def close_listing(request, listing_id):
    user_obj = request.user
    listing_obj = AuctionListing.objects.filter(id=listing_id).first()

    close_listing_helper(user_obj, listing_obj, closed_by_user=True)
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

@login_required
@require_POST
def post_comment(request, listing_id):
    print(listing_id)
    print(request.POST)
    form = CreateCommentForm(request.POST)
    if form.is_valid():
        listing_obj = AuctionListing.objects.filter(id=listing_id).first()
        print(listing_obj)

        comment = form.save(commit=False)
        comment.user_fk = request.user
        comment.listing_fk = listing_obj
        comment.save()

    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

def categories(request):
    categories_dict = {choice.value: choice.label for choice in ListingCategories}
    print(categories_dict)
    print(type(categories_dict))
    return render(request, "auctions/categories.html",
        {
            'categories_dict':categories_dict
        }
    )

def category(request, category_enum):
    category_name = {choice.value: choice.label for choice in ListingCategories}[category_enum]
    listings = AuctionListing.objects.filter(category=category_enum).all()
    return render(request, "auctions/category.html",
        {
            'category':category_name,
            'listings':listings,
        }
    )
