from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Game', 'Game'),
        ('Console', 'Console'),
        ('Accessory', 'Accessory'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  # product details/description
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')

    class Meta:
        unique_together = ('user', 'product')  # prevent duplicate wishlist entries

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_carts')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')  # prevent duplicate cart entries

    def __str__(self):
        return f"{self.user.username} - {self.product.name} (x{self.quantity})"

    def get_total_price(self):
        return self.quantity * self.product.price


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    ordered_at = models.DateTimeField(auto_now_add=True)

    # Added default values to avoid migration issues
    full_name = models.CharField(max_length=100, default="Not Provided")
    address = models.TextField(default="Not Provided")
    phone = models.CharField(max_length=15, default="Not Provided")

    def __str__(self):
        return f"{self.user.username} ordered {self.product.name} on {self.ordered_at.strftime('%Y-%m-%d')}"
