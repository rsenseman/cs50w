from django.forms import ModelForm, DateInput

from .models import AuctionListing, Bid, Comment

class MyDateInput(DateInput):
    input_type = 'date'

class CreateListingForm(ModelForm):
    class Meta:
        model = AuctionListing
        fields = [
            'title',
            'description',
            'image_url',
            'minimum_bid',
            'auction_start_time',
            'auction_end_time',
            'category',
        ]
        widgets = {
            'auction_start_time': MyDateInput(),
            'auction_end_time': MyDateInput(),
        }

class IssueBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = [
            'amount',
        ]

class CreateCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            'content',
        ]
