from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.generic import CreateView,View,TemplateView,ListView,UpdateView,DetailView
from django.contrib.auth import authenticate, login,logout
from django.utils.decorators import method_decorator


from adminapi.models import Spice,Seller,Bid


def signin_required(fn):    
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"invalid session!..please login")
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

def is_admin(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_superuser:
            messages.error(request,"Permission denied for current user !")
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

decs=[signin_required,is_admin]


class SignInView(View):
    template_name="login.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    
    def post(self, request, *args, **kwargs):
        uname = request.POST.get("username")
        pwd = request.POST.get("password")
        if uname and pwd:
            usr = authenticate(request, username=uname, password=pwd)
            if usr is not None:
                login(request, usr)
                messages.success(request, "Login success")
                return redirect("home")
        
        messages.error(request, "Failed to login")
        return render(request, self.template_name)
    

@method_decorator(decs,name="dispatch")   
class HomeView(TemplateView):
    template_name="home.html"
    
@method_decorator(decs,name="dispatch") 
class BidsView(ListView):
    template_name="bids.html"
    model=Bid
    context_object_name="bids"
    
    
def signoutview(request,*args,**kwargs):
    logout(request)
    return redirect("signin")