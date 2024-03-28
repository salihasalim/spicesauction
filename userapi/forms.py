from django import forms
from  adminapi.models import Seller,Spice,Auction,Bid
from django.contrib.auth.forms import UserCreationForm


class RegForm(UserCreationForm):
    class Meta:
        model=Seller
        fields=["name","id_proof","profile","address","phone","email_address","username","password1","password2"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Address', 'rows': 3}),
            'phone': forms.NumberInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Phone'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Email Address'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Reenter password'}),

        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None

class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)
    
class AddProducts(forms.ModelForm):
    class Meta:
        model=Spice
        fields=["name","description","stock_quantity","image"]
        widgets={
            "name":forms.TextInput(attrs={"class":"form-control"}),
            "description":forms.Textarea(attrs={"class":"form-control","rows":3}),
            "stock_quantity":forms.NumberInput(attrs={"class":"form-control"}),
        }
        
        
class AddAuction(forms.ModelForm):
    class Meta:
        model=Auction
        fields=["starting_bid","expected_bid","number_of_lots","end_time"]
        widgets={
            "starting_bid":forms.NumberInput(attrs={"class":"form-control"}),
            "expected_bid":forms.NumberInput(attrs={"class":"form-control"}),
            "number_of_lots":forms.NumberInput(attrs={"class":"form-control"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"})
        }
        
        
class AddBid(forms.ModelForm):
    class Meta:
        model=Bid
        fields=["amount"]
        widgets={
            "amount":forms.NumberInput(attrs={"class":"form-control"}),
        }