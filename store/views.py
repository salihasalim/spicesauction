from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect, render
from django.views.generic import View, TemplateView, FormView
import razorpay
from store.forms import OrderForm
from store.models import BasketItem, OrderItem, Spice, ProcessingType, CustomUser, Order, Basket
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import os
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import stripe
from django.conf import settings

stripe.api_key = "your_stripe_secret_key"

class StripeCheckoutView(View):
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs.get("order_id"))
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {'name': 'Spices Order'},
                    'unit_amount': int(order.order_total * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('store:stripe-success', args=[order.id])),
            cancel_url=request.build_absolute_uri(reverse('store:stripe-cancel', args=[order.id])),
        )

        order.stripe_payment_intent_id = session.payment_intent
        order.save()

        return redirect(session.url)
# Create your views here.
def render_razor_page(request):
    return render(request, 'razorpay.html')

class SpiceListView(View):
    
    template_name = "index.html"
    
    def get(self, request, *args, **kwargs):
        print("SpiceListView is called!") 
        
        qs = Spice.objects.all()
        
        p = Paginator(qs, 4)
        
        page_number = request.GET.get('page')
        
        try:
            page_obj = p.get_page(page_number)
        except PageNotAnInteger:
            page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)
        context = {'page_obj': page_obj}
            
        return render(request, self.template_name, context)

class SpiceDetailView(View):
    template_name = "spice-detail.html"
    
    def get(self, request, *args, **kwargs):
        
        id = kwargs.get("pk")
        qs = Spice.objects.get(id=id)
        
        return render(request, self.template_name, {"data": qs})
        
class AddtoCartView(View):
        
    def post(self, request, *args, **kwargs):
        
        id = kwargs.get("pk")
        
        quantity = request.POST.get("quantity")
        
        spice_object = Spice.objects.get(id=id)
        
       
        
        if not hasattr(request.user, 'cart'):
            new_cart = Basket.objects.create(user=request.user)
            # Refresh the user instance to make sure the relationship is updated
            request.user.refresh_from_db()
        basket_object = request.user.cart
        
        BasketItem.objects.create(
            spice_object=spice_object,
            quantity=quantity,
            basket_object=basket_object,
        )
        print("item added")
        
        return redirect('store:cart-summary')  
        
class CartSummaryView(View):
    template_name = "cart_summary.html"
    
    def get(self, request, *args, **kwargs):
        
        if not hasattr(request.user, 'cart'):
            # Create a new cart for this user
            new_cart = Basket.objects.create(user=request.user)
            # Refresh the user instance to make sure the relationship is updated
            request.user.refresh_from_db()
        
        qs = BasketItem.objects.filter(basket_object=request.user.cart, is_order_placed=False)
        
        basket_item_count = qs.count()
        
        basket_total = sum([bi.item_total for bi in qs])
        
        return render(request, self.template_name, {"basket_items": qs, "basket_total": basket_total, "basket_item_count": basket_item_count})
            
class DeleteCartItemView(View):
        
    def get(self, request, *args, **kwargs):
        
        id = kwargs.get("pk")
        
        BasketItem.objects.get(id=id).delete()
        messages.success(request, "Item removed")
        return redirect("store:cart-summary")
            
from django.http import JsonResponse
import razorpay

import razorpay
from django.shortcuts import render
from django.http import JsonResponse
from .models import Order  # Ensure you import your Order model

class PlaceHolderView(View):
    
    template_name = "place_order.html"
    
    form_class = OrderForm
    def get(self, request, *args, **kwargs):
        
        form_instance = self.form_class()
        
        qs = request.user.cart.cart_item.filter(is_order_placed=False)
        
        total = sum([bi.item_total for bi in qs])
        
        return render(request, self.template_name, {"form": form_instance, "items": qs, "total": total})
    
    def post(self, request, *args, **kwargs):
        form_data = request.POST
        form_instance = self.form_class(form_data)
        
        if form_instance.is_valid():
            form_instance.instance.customer = request.user
            order_instance = form_instance.save()
            
            basket_items = request.user.cart.cart_item.filter(is_order_placed=False)
            payment_method = form_instance.cleaned_data.get("payment_method")
            
            if payment_method == "ONLINE":
                try:
                    # Use the same key consistently
                    client = razorpay.Client(auth=("settings.RZP_KEY_ID", "settings.RZP_KEY_SECRET"))  # Add your Razorpay key here
                    
                    total = int(sum([bi.item_total for bi in basket_items]) * 100)

                    data = {
                        "amount": total,
                        "currency": "INR",
                        "receipt": f"order_{order_instance.id}"
                    }
                    
                    payment = client.order.create(data=data)
                    
                    order_instance.rzp_order_id = payment['id']
                    order_instance.save()
                    
                    context = {
                        "amount": total,
                        "key_id": "settings.RZP_KEY_ID",  # Use the same key as above
                        "order_id": payment['id'],
                        "currency": "INR",
                        "callback_url": request.build_absolute_uri(reverse('store:payment-verify')),
                        "name": "Spice Store",
                        "description": "Order Payment",
                        "user": request.user
                    }
                    
                    return render(request, "payment.html", context)
                    
                except Exception as e:
                    print(f"Payment Error: {str(e)}")
                    messages.error(request, "Payment initialization failed")
                    return redirect('store:cart-summary')
        
        return redirect('store:productlist')               
        
class OrderSummaryView(View):
    
    template_name = "order_summary.html"
    
    def get(self, request, *args, **kwargs):
        
        qs = reversed(request.user.orders.all())
        
        return render(request, self.template_name, {"orders": qs})   

@method_decorator(csrf_exempt, name="dispatch") 
class PaymentVerificationView(View):
    def post(self, request, *args, **kwargs):
        try:
            client = razorpay.Client(auth=("settings.RZP_KEY_ID", "settings.RZP_KEY_SECRET"))
            
            # Get payment verification data
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')

            # Create parameters dictionary
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }

            try:
                # Verify signature
                client.utility.verify_payment_signature(params_dict)
                
                # Update order status
                order = Order.objects.get(rzp_order_id=order_id)
                order.payment_id = payment_id
                order.is_paid = True
                order.save()
                
                messages.success(request, "Payment successful!")
                return redirect('store:order-summary')
                
            except Exception as e:
                print(f"Signature Verification Error: {str(e)}")
                messages.error(request, "Payment verification failed!")
                return redirect('store:cart-summary')
                
        except Exception as e:
            print(f"Payment Processing Error: {str(e)}")
            messages.error(request, "Payment processing failed!")
            return redirect('store:cart-summary')
    
    from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Test view is working!")