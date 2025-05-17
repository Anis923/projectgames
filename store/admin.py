from django.contrib import admin
from .models import Product, Wishlist, CartItem, Order

admin.site.register(Product)
admin.site.register(Wishlist)
admin.site.register(CartItem)
admin.site.register(Order)
