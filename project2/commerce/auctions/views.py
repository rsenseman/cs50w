from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import CreateListingForm, IssueBidForm
from .models import AuctionListing, Bid, User


def index(request):
    user_listings = AuctionListing.objects.filter(user_fk=request.user)
    return render(request, "auctions/index.html", {'listings':user_listings})


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
    show_bid_ui = request.user.is_authenticated

    max_bid_if_exists = Bid.objects.filter(listing_fk=listing).order_by('-amount').first() # may return None
    max_bid = max_bid_if_exists.amount if max_bid_if_exists is not None else listing.minimum_bid

    class IssueBidFormListingAware(IssueBidForm):
        def clean(self):
            cleaned_data = super().clean()
            bid_amount = float(self['amount'].value())
            if bid_amount <= max_bid:
                raise ValidationError(
                    f"New bid must be higher than existing highest bid: {max_bid}"
                )


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
                    'show_bid_ui': show_bid_ui,
                    'listing': listing,
                    'max_bid': max_bid,
                }
            )
    else:
        return render(request, "auctions/listing.html",
            {
                'form': IssueBidFormListingAware,
                'show_bid_ui': show_bid_ui,
                'listing': listing,
                'max_bid': max_bid,
            }
        )


@login_required
def watchlist(request):
    pass
