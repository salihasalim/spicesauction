from django.urls import path
from adminapi import views



urlpatterns=[
    
    path("login/",views.SignInView.as_view(),name="signin"),
    path("logout/",views.signoutview,name="signout"),
    path("home/",views.HomeView.as_view(),name="home"),
    path("bids/",views.BidsView.as_view(),name="bids"),



]