from django.shortcuts import render,redirect
from adminapi.models import Seller,Spice
from django.contrib import messages
from django.views.generic import CreateView,FormView,ListView,UpdateView,DetailView,TemplateView





def homepage(request):
    return render (request,"home.html")

def loginpage(request):
     return render(request,"loginpage.html")


def saveuser(request):
    if request.method=="POST":
        fname=request.POST.get('fname')
        lname=request.POST.get('lname')
        email=request.POST.get('email')
        mobile=request.POST.get('fname')
        password=request.POST.get('password')
        username=request.POST.get('username')
        doc=request.FILES['doc']
        obj=user(firstname=fname,lastname=lname,phone=mobile,email_address=email,id_proof=doc,password=password,username=username)
        obj.save()
        return redirect(loginpage)
    

def login_user(request):
    if request.method == "POST":
        em = request.POST.get('username')
        pwd = request.POST.get('password')
        messages.success(request, "Login succesfully...!!")
        if Seller.objects.filter(username=em,password=pwd).exists():
                request.session['username']=em
                request.session['password']=pwd
                return redirect(homepage)
        else:
            return redirect(loginpage)
    else:
        return redirect(loginpage)


    
# @method_decorator(decs,name="dispatch")
class SpiceListView(ListView):
    template_name="home.html"    
    model=Spice
    context_object_name="spices"   
          


def logoutuser(request):
    del request.session['username']
    del request.session['password']
    return redirect(loginpage)




