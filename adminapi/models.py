from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class CustomUser(AbstractUser):
    user_type_choices = [ 
        ('Admin', 'Admin'),
        ('Seller', 'Seller'),
    ]
    user_type = models.CharField(max_length=50, choices=user_type_choices, default='Admin') 

class SuperAdmin(CustomUser):
    phone = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True, null=True)

class Seller(CustomUser):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email_address = models.EmailField()
    address = models.CharField(max_length=100, null=True)
    id_proof = models.FileField(null=True, upload_to="images")
    profile = models.ImageField(upload_to="images", null=True)
    is_available = models.BooleanField(default=True, null=True)

    def __str__(self):
        return self.name

class Spice(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    stock_quantity = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to="images", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=100,)

    def __str__(self):
        return self.name 


class Auction(models.Model):
    spice = models.ForeignKey(Spice, on_delete=models.CASCADE)
    auctioneer = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='auctions_auctioneer', null=True)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
    number_of_lots = models.IntegerField(default=1)
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    winner = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='auctions_winner', null=True)

    def update_highest_bid_of_day(self):
        today = timezone.now().date()
        bids_today = self.bid_set.filter(timestamp__date=today)
        if bids_today:
            highest_bid = max(bids_today, key=lambda bid: bid.amount)
            self.current_bid = highest_bid.amount
        else:
            self.current_bid = self.starting_bid
        self.save()


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bidder = models.ForeignKey(Seller, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of {self.amount} by {self.bidder.username}"
