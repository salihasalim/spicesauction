from django.shortcuts import render,redirect
from django.views import View
from adminapi.models import Seller,Spice,Bid,Auction,Payment,Feedbacks
from django.contrib import messages
from django.views.generic import CreateView,FormView,ListView,UpdateView,DetailView,TemplateView
from django.urls import reverse_lazy
from userapi.forms import RegForm,LoginForm,AddProducts,AddAuction,AddBid,AddFeedback
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from reportlab.pdfgen import canvas
import io
from django.utils import timezone



def signin_required(fn):    
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"invalid session!..please login")
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper




class RegView(CreateView):
    template_name = "user/register.html"
    model= Seller
    form_class = RegForm
    success_url=reverse_lazy("signin")


    def form_valid(self, form):
        form.instance.user_type = 'Seller'
        return super().form_valid(form)   
 
    

class SignInView(FormView):
    template_name="user/loginpage.html"
    form_class=LoginForm
    
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=uname,password=pwd)
            if usr:
                login(request,usr)
                messages.success(request,"login success")
                return redirect("auctions-list")
            else:
                messages.error(request,"failed to login")
                return render(request,self.template_name,{"form":form})
            
from django.db.models import Sum           
               
class AuctionsListView(ListView):
    template_name="user/home.html"    
    model=Auction
    context_object_name="auctions" 
    
    def get_queryset(self):
        return Auction.objects.filter(status='Available')  
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        highest_bid = Bid.objects.order_by('-amount').first()

        context['highestbid'] = highest_bid
        return context

        
    
    

class BidsListView(ListView):
    template_name="user/bids.html"
    model=Bid
    context_object_name="bids"

    def get_queryset(self):
        user_id = self.request.user.id
        print(user_id)
        return Bid.objects.filter(auction__auctioneer_id=user_id)

    

class ProductsListView(ListView):
    template_name="user/products.html"
    form_class=AddProducts
    model=Spice
    context_object_name="spices"
    
    def get_queryset(self):
        user_id = self.request.user.id
        print(user_id)
        return Spice.objects.filter(seller=user_id)
    

class ProductsAddView(CreateView):
    template_name="user/addproducts.html"
    form_class=AddProducts
    model=Spice
    success_url=reverse_lazy("products-list")

    def form_valid(self, form):
        seller_instance = get_object_or_404(Seller, pk=self.request.user.id)
        form.instance.seller = seller_instance
        messages.success(self.request, "Product added successfully")
        return super().form_valid(form)

    
    def form_invalid(self, form):
        messages.error(self.request, "Product adding failed")
        return super().form_invalid(form)
    

def remove_product(request,*args,**kwargs):
    id=kwargs.get("pk")
    Spice.objects.filter(id=id).delete()
    return redirect("products-list") 


class AuctionAddView(CreateView):
    template_name="user/addauction.html"
    form_class=AddAuction
    model=Auction
    success_url=reverse_lazy("products-list")

    def form_valid(self, form):
        seller_instance = get_object_or_404(Seller, pk=self.request.user.id)
        id=self.kwargs.get("pk")
        spice=Spice.objects.get(id=id)
        form.instance.auctioneer = seller_instance
        form.instance.spice = spice
        messages.success(self.request, "Auction added successfully")
        return super().form_valid(form)

    
    def form_invalid(self, form):
        messages.error(self.request, "Auction adding failed")
        return super().form_invalid(form)
    

from django.db.models import Max

class place_bid(CreateView):
    template_name="user/addbid.html"
    form_class=AddBid
    model=Bid
    success_url=reverse_lazy("auctions-list")

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        auction_id = self.kwargs.get("pk")
        auction = get_object_or_404(Auction, id=auction_id)
        bidder_id = self.request.user.id
        bidder = get_object_or_404(Seller, id=bidder_id)
        form.instance.auction = auction
        form.instance.bidder = bidder 
        bid = form.save() 
        
        if float(amount) >= float(auction.expected_bid):
            auction.spice.status = 'Not Available'
            auction.status = 'Sold'
            bid.is_selected = True
            auction.save()
            bid.save()
            auction.spice.save()
        
        messages.success(self.request, "Bid placed successfully")
        return super().form_valid(form)

    
    def form_invalid(self, form):
        messages.error(self.request, "Bid adding failed")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auction_id = self.kwargs.get("pk")
        auction = get_object_or_404(Auction, id=auction_id)
        context['auction'] = auction
        high_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        if high_bid:
            context['highbid'] = high_bid.amount
        else:
            context['highbid'] = None
    
        return context


class WonbidsView(ListView):
    template_name="user/wonbids.html"
    model=Bid
    context_object_name="bids"
    
    def get_queryset(self):
        user_id = self.request.user.id
        return Bid.objects.filter(bidder=user_id, is_selected=True)
    

import json
from django.http import JsonResponse

def create_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        buyer_id = data.get('buyer_id')
        bid_id = data.get('bid_id')

        print("Data received from front end:", data)

        try:
            payment = Payment.objects.create(
                user_id=buyer_id,
                bid_id=bid_id,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)



    


def download_bill(request, bid_id):
    bid = Bid.objects.get(id=bid_id)
    spice_name = bid.auction.spice.name
    unitprice = bid.amount
    user_name = bid.bidder.seller.name
    date=timezone.now()
    quantity=bid.auction.spice.stock_quantity
    amount=unitprice*quantity
    auction=bid.auction.auctioneer
    

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Spice Auction Bill")
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Thank you for purchasing {spice_name} from our site.")
    p.drawString(100, 700, f"Auctioneer : {auction}")
    p.drawString(100, 680, f"User: {user_name}")
    p.drawString(100, 660, f"Date: {date}")
    p.drawString(100, 640, f"Quantity: {quantity}")
    p.drawString(100, 620, f"Unit Price: {unitprice}")
    p.drawString(100, 580, f"___________________________________")
    p.drawString(100, 550, f"Total Price: Rs. {amount}")
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="spice_auction_bill.pdf"'

    return response

def download_slip(request, bid_id):
    bid = Bid.objects.get(id=bid_id)
    spice_name = bid.auction.spice.name
    amount = bid.amount
    user_name = bid.bidder.seller.name

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Spice Auction Bill.. payment slip")
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"{spice_name}.")
    p.drawString(100, 700, f"Amount: Rs. {amount}")
    p.drawString(100, 680, f"User: {user_name}")
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="spice_auction_bill.pdf"'

    return response
      

class AddfeedbackView(CreateView):
    template_name="user/feedback.html"
    form_class=AddFeedback
    model=Feedbacks
    success_url=reverse_lazy("auctions-list")
 
 
    def form_valid(self, form):
        seller_instance = get_object_or_404(Seller, pk=self.request.user.id)
        form.instance.user = seller_instance
        messages.success(self.request, "Feedback added successfully")
        return super().form_valid(form)

    
    def form_invalid(self, form):
        messages.error(self.request, "Feedback adding failed")
        return super().form_invalid(form)


def logoutuser(request,*args,**kwargs): 
    logout(request)
    return redirect('signin')




