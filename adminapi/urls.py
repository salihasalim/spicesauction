from django.urls import path
from adminapi import views



urlpatterns=[
    path("login/",views.SignInView.as_view(),name="adminsignin"),
    path("logout/",views.signoutview,name="adminsignout"),
    path("home/",views.HomeView.as_view(),name="home"),
    path("bids/",views.BidsView.as_view(),name="bids"),
    path("products/",views.ProductsView.as_view(),name="products"),
    path("sellers/",views.CustomerView.as_view(),name="sellers"),
    path("feedbacks/",views.FeedbacksView.as_view(),name="feedbacks"),
    path("auctions/",views.AuctionsView.as_view(),name="auctions"),
    path("payments/",views.PaymentsView.as_view(),name="payments"),




]