from django.urls import path
from userapi import views
from django.conf import settings
from django.conf.urls.static import static
from .views import get_highest_bids
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/',views.RegView.as_view(),name="signup"),
    path('',views.SignInView.as_view(),name="signin"),
    path("buysign/",views.BuyerSignInView.as_view(), name="buyersign"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="password_reset.html"), name="password_reset"),
    
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="password_reset_done.html"), name="password_reset_done"),
    
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="password_reset_confirm.html"), name="password_reset_confirm"),
    
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="password_reset_complete.html"), name="password_reset_complete"),
        
    path('logout/',views.logoutuser,name="logout"),
    path("auctions/",views.AuctionsListView.as_view(),name="auctions-list"),
    path("bid/",views.BidsListView.as_view(),name="bid-list"),
    path('running-auctions/',views.RunningAuctionsListView.as_view(), name='running-auctions'),
    path("get-highest-bids/", get_highest_bids, name="get-highest-bids"),
    path("products/",views.ProductsListView.as_view(),name="products-list"),
    path("products/add/",views.ProductsAddView.as_view(),name="products-add"),
    path("products/<int:pk>/remove/",views.remove_product,name="products-remove"),
    path("products/<int:pk>/add/",views.AuctionAddView.as_view(),name="auction-add"),
    path('place-bid/<int:pk>/', views.place_bid.as_view(), name='place_bid'),
    path("wonbids/",views.WonbidsView.as_view(),name="wonbids"),
    path("makepayment/",views.create_payment,name="payment"),
    path('download-bill/<int:bid_id>/', views.download_bill, name='download_bill'),
    path('download-slip/<int:bid_id>/', views.download_slip, name='download_slip'),
    path("feedback/",views.AddfeedbackView.as_view(),name="feedback-add"),
    





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
