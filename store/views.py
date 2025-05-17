from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from .models import Product, Wishlist, CartItem, Order
from .forms import ProductForm, CheckoutForm


# Home View (login required)
@login_required
def home(request):
    return render(request, 'store/home.html')


# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f"Welcome back, {form.get_user().username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


# Signup View
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})


# Logout View
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# Products View
@login_required
def products(request):
    category = request.GET.get('category')
    if category in ['Game', 'Console', 'Accessory']:
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    return render(request, 'store/products.html', {
        'products': products,
        'selected_category': category,
        'user': request.user,
    })


# Wishlist Views
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"Added {product.name} to your wishlist.")
    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, product_id):
    deleted, _ = Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    if deleted:
        messages.success(request, "Item removed from wishlist.")
    return redirect('wishlist')


@login_required
def add_to_cart_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"Moved {product.name} from wishlist to cart.")
    return redirect('wishlist')


# Cart Views
@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    cart_total = sum(item.get_total_price() for item in cart_items)
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect('cart')


@login_required
def remove_from_cart(request, product_id):
    deleted, _ = CartItem.objects.filter(user=request.user, product_id=product_id).delete()
    if deleted:
        messages.success(request, "Item removed from cart.")
    return redirect('cart')


# Checkout View
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            address = form.cleaned_data['address']
            phone = form.cleaned_data['phone']

            for item in cart_items:
                Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    ordered_at=timezone.now(),
                    full_name=full_name,
                    address=address,
                    phone=phone,
                )

            cart_items.delete()
            messages.success(request, "Your order has been placed successfully!")
            return redirect('profile')
    else:
        form = CheckoutForm()

    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form,
    })


# Profile View
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).select_related('product').order_by('-ordered_at')
    return render(request, 'store/profile.html', {'orders': orders})


# Admin: Add Product
@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('products')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


# Admin: View All Users & Their Orders
@staff_member_required
def view_users_orders(request):
    users = User.objects.filter(is_superuser=False).prefetch_related('orders__product')
    return render(request, 'store/view_users_orders.html', {'users': users})


# Admin: Remove Product
@staff_member_required
@require_POST
def remove_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, f"Product '{product.name}' removed successfully.")
    return redirect('products')


# Admin: Edit Product
@staff_member_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('products')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'store/edit_product.html', {'form': form, 'product': product})