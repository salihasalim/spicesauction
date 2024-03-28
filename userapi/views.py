from django.shortcuts import render,redirect
from adminapi.models import Seller,Spice,Bid,Auction
from django.contrib import messages
from django.views.generic import CreateView,FormView,ListView,UpdateView,DetailView,TemplateView
from django.urls import reverse_lazy
from userapi.forms import RegForm,LoginForm,AddProducts,AddAuction,AddBid
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import get_object_or_404




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
            
            
               
# @method_decorator(decs,name="dispatch")
class AuctionsListView(ListView):
    template_name="user/home.html"    
    model=Auction
    context_object_name="auctions"   
    

# @method_decorator(decs,name="dispatch")
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
    
    
class BidAddView(CreateView):
    template_name="user/addauction.html"
    form_class=AddBid
    model=Bid
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
          


def logoutuser(request,*args,**kwargs): 
    logout(request)
    return redirect('signin')




