from django.urls import path
from adminapi import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns=[
    
    path("login/",views.SignInView.as_view(),name="signin"),
    path("logout/",views.signoutview,name="signout"),
    path("home/",views.HomeView.as_view(),name="home"),
    path("bids/",views.BidsView.as_view(),name="bids"),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)