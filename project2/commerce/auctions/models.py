from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    watched = models.ManyToManyField('AuctionListing')

class ListingCategories(models.TextChoices):
    EM = 'em', 'eBay Motors'
    E = 'e', 'Electronics'
    CA = 'ca', 'Collectibles & Art'
    HG = 'hg', 'Home & Garden'
    CSA = 'csa', 'Clothing, Shoes & Accessories'
    TH = 'th', 'Toys & Hobbies'
    SG = 'sg', 'Sporting Goods'
    BMM = 'bmm', 'Books, Movies & Music'
    HB = 'hb', 'Health & Beauty'
    BI = 'bi', 'Business & Industrial'
    JW = 'jw', 'Jewelry & Watches'
    BE = 'be', 'Baby Essentials'
    PS = 'ps', 'Pet Supplies'
    O = 'o', 'Other'

class AuctionListing(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    image_url = models.URLField(max_length=300, null=True, blank=True)
    minimum_bid = models.DecimalField(max_digits=8, decimal_places=2)
    auction_start_time = models.DateTimeField()
    auction_end_time = models.DateTimeField()
    category = models.CharField(max_length=30, choices=ListingCategories.choices)

    def clean(self):
        if not (self.auction_end_time > self.auction_start_time):
            raise ValidationError("Auction end time must be after start time")

class Bid(models.Model):
    listing_id = models.ForeignKey('AuctionListing', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

class Comment(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    lisiting_id = models.ForeignKey('AuctionListing', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=300)
