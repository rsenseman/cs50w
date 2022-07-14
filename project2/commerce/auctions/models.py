from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    watched = models.ManyToManyField('AuctionListing')

class ListingCategories(models.TextChoices):
    EM = 'eBay Motors'
    E = 'Electronics'
    CA = 'Collectibles & Art'
    HG = 'Home & Garden'
    CSA = 'Clothing, Shoes & Accessories'
    TH = 'Toys & Hobbies'
    SG = 'Sporting Goods'
    BMM = 'Books, Movies & Music'
    HB = 'Health & Beauty'
    BI = 'Business & Industrial'
    JW = 'Jewelry & Watches'
    BE = 'Baby Essentials'
    PS = 'Pet Supplies'
    O = 'Other'

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
        if not (auction_end_time > auction_start_time):
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
