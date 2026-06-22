from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Review(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField()

    review_image = models.ImageField(
        upload_to="reviews/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
# ========================
# PRODUCT MODEL
# ========================
class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Skincare", "Skincare"),
        ("Makeup", "Makeup"),
        ("Accessories", "Accessories"),
        ("Clothing", "Clothing"),
    ]

    SKIN_CHOICES = [
        ("oily", "Oily"),
        ("dry", "Dry"),
        ("combination", "Combination"),
        ("sensitive", "Sensitive"),
    ]

    FASHION_CHOICES = [
        ("casual", "Casual"),
        ("street", "Street Style"),
        ("luxury", "Luxury"),
        ("minimal", "Minimal"),
    ]

    CLASS_CHOICES = [
        ("elegant", "Elegant"),
        ("bold", "Bold"),
        ("royal", "Royal"),
        ("modern", "Modern Chic"),
    ]

    COLLECTION_CHOICES = [
        ("kbeauty", "K-Beauty"),
        ("genz", "Gen Z"),
        ("wedding", "Wedding"),
        ("everyday", "Everyday Beauty"),
        ("festive", "Festive Glow"),
    ]

    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="Skincare"
    )
    collection = models.CharField(
        max_length=20, choices=COLLECTION_CHOICES, null=True, blank=True
    )
    skin_type = models.CharField(
        max_length=20, choices=SKIN_CHOICES, null=True, blank=True
    )
    fashion_type = models.CharField(
        max_length=20, choices=FASHION_CHOICES, null=True, blank=True
    )
    class_type = models.CharField(
        max_length=20, choices=CLASS_CHOICES, null=True, blank=True
    )

    stock = models.IntegerField(default=10)
    customizable = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ========================
# ORDER MODEL (MAIN ORDER)
# ========================
class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


# ========================
# ORDER ITEMS (MULTIPLE PRODUCTS PER ORDER)
# ========================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# ========================
# USER PREFERENCE (QUIZ DATA)
# ========================
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.preference}"


# ========================
# CART
# ========================
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


# ========================
# WISHLIST
# ========================
class WishlistItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return self.product.name
