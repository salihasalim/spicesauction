from django.urls import path
from userapi import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('homepage/',views.homepage,name="homepage"),
    path('',views.loginpage,name="loginpage"),
    path('saveuser/',views.saveuser,name="saveuser"),
    path('login_user/',views.login_user,name="login_user"),
    path('logout_user/',views.logoutuser,name="logout_user"),
    path("spice/",views.SpiceListView.as_view(),name="spice-list"),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)