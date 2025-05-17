from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),

    path('products/', views.products, name='products'),

    # Wishlist URLs
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/add-to-cart/<int:product_id>/', views.add_to_cart_from_wishlist, name='add_to_cart_from_wishlist'),

    # Cart URLs
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('profile/', views.profile, name='profile'),

    # Admin URLs
    path('dashboard/view-orders/', views.view_users_orders, name='view_users_orders'),
    path('add-product/', views.add_product, name='add_product'),

    path('product/<int:product_id>/remove/', views.remove_product, name='remove_product'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
]
