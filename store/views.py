from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404
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
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


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
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
        
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

from django.db import transaction
from django.urls import reverse
from django.shortcuts import render, redirect
from django.db import transaction
from django.conf import settings
from django.contrib import messages
import razorpay
from .models import BasketItem, Order, OrderItem, Basket
from .forms import OrderForm
from django.urls import reverse

class PlaceHolderView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    template_name = "place_order.html"
    form_class = OrderForm
    

    def get(self, request, *args, **kwargs):
        form_instance = self.form_class()
        print('==========hai')
        print(request.user)

        spice_id = request.GET.get("id")
        qty = request.GET.get('quantity')  # Fetch `id` from query parameters
        s = None


        if spice_id and qty:  # Only fetch and create BasketItem if id is provided
            try:
                s = Spice.objects.get(id=spice_id)
                BasketItem.objects.create(spice_object=s, quantity=qty, basket_object=request.user.cart)
            except Spice.DoesNotExist:
                return HttpResponse("Invalid Spice ID", status=400)

        qs = BasketItem.objects.filter(basket_object=request.user.cart, is_order_placed=False)

        total = sum([bi.item_total for bi in qs])  # Total of the cart items
        print(total)
        return render(request, self.template_name, {"form": form_instance, "items": qs, "total": total,"s":s})

    def post(self, request, *args, **kwargs):
        form_data = request.POST
        form_instance = self.form_class(form_data)

        if form_instance.is_valid():
            form_instance.instance.customer = request.user
            order_instance = form_instance.save()

            # Fetch basket items that haven't been ordered yet
            basket_items = request.user.cart.cart_item.filter(is_order_placed=False)
            print("basket", basket_items)

            payment_method = form_instance.cleaned_data.get("payment_method")
            print("method", payment_method)

            # Process payment if it's online
            print()
            if payment_method == "ONLINE":
                try:
                    # Initialize Razorpay client
                    client = razorpay.Client(auth=("rzp_test_IzIBFTmzd3zzKk", "mMvIdZd7a4EU1pMd9tSQEbE0"))
                    print(client)

                    total_in_paise = float(sum([bi.item_total for bi in basket_items])*100)  # Amount in paise
                    print(total_in_paise)
                    data = {
                        "amount": total_in_paise,
                        "currency": "INR",
                        "receipt": f"order_{order_instance.id}"
                    }

                    # Create a Razorpay order
                    payment = client.order.create(data=data)
                    with transaction.atomic():
                    # Create OrderItems for each BasketItem
                        for basket_item in basket_items:
                            OrderItem.objects.create(
                                order_object=order_instance,  # Set the order for the item
                                spice_object=basket_item.spice_object,
                                quantity=basket_item.quantity,
                                price=basket_item.spice_object.price
                            )

                            # Mark the basket item as ordered
                            basket_item.is_order_placed = True
                            basket_item.save()

                        # Set the basket for the order
                        bas = get_object_or_404(Basket, id=request.user.cart.id)
                        print("mmmmmmmmmmmmm", bas)
                        order_instance.baskets = bas

                        # Set the order as paid and update the status to "Completed"
                        order_instance.is_paid = True
                        order_instance.status = "Completed"
                        
                        # Save Razorpay order ID to the order instance
                        order_instance.rzp_order_id = payment['id']
                        order_instance.save()

                    # Context for the payment page
                    context = {
                        "amount": total_in_paise,  # Pass the amount in paise (already multiplied by 100)
                        "key_id": "rzp_test_IzIBFTmzd3zzKk",  # Use actual Razorpay Key ID
                        "order_id": payment['id'],
                        "currency": "INR",
                        "callback_url": request.build_absolute_uri(reverse('store:payment-verify')),
                        "name": "Spice Store",
                        "description": "Order Payment",
                        "user": request.user
                    }

                    # Render payment page for online payment
                    return render(request, "razorpay.html", context)

                except Exception as e:
                    print(f"Payment Error: {str(e)}")
                    messages.error(request, "Payment initialization failed")
                    return redirect('store:cart-summary')

            else:  # Handling case for other payment methods (like 'CASH' or others)
                # Using a transaction to ensure that all items are ordered correctly
                with transaction.atomic():
                    # Create OrderItems for each BasketItem
                    for basket_item in basket_items:
                        OrderItem.objects.create(
                            order_object=order_instance,  # Set the order for the item
                            spice_object=basket_item.spice_object,
                            quantity=basket_item.quantity,
                            price=basket_item.spice_object.price
                        )

                        # Mark the basket item as ordered
                        basket_item.is_order_placed = True
                        basket_item.save()

                    # Set the basket for the order
                    bas = get_object_or_404(Basket, id=request.user.cart.id)
                    print("mmmmmmmmmmmmm", bas)
                    order_instance.baskets = bas

                    # Set the order as paid and update the status to "Completed"
                    order_instance.is_paid = True
                    order_instance.status = "Completed"
                    order_instance.save()

                    # Success message and redirect to the order summary page
                    messages.success(request, "Your order has been placed successfully!")
                    return redirect('store:order-summary')

        # In case the form is not valid, redirect to cart page
        messages.error(request, "There was an error with your order. Please try again.")
        return redirect('store:cart-summary')


          
        
class OrderSummaryView(View):
    template_name = "order_summary.html"
    
    def get(self, request, *args, **kwargs):
        # Filter orders based on the 'Completed' status
        qs = Order.objects.filter(customer=request.user, status="Completed").order_by('-created_at')  # Corrected status value
        print(qs)
        
        if not qs.exists():
            messages.info(request, "You have no completed orders.")
        
        # Fetch all the OrderItems for the orders in the queryset 'qs'
        items = OrderItem.objects.filter(order_object__in=qs)  # Use '__in' to filter based on multiple orders
        
        return render(request, self.template_name, {"orders": qs, "items": items})


@method_decorator(csrf_exempt, name="dispatch") 
class PaymentVerificationView(View):
    def post(self, request, *args, **kwargs):
        try:
            client = razorpay.Client(auth=("rzp_test_IzIBFTmzd3zzKk", "mMvIdZd7a4EU1pMd9tSQEbE0"))
            
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


def about(request):
    return render(request,'about.html')



def contact(request):
    return render(request,'contact.html')