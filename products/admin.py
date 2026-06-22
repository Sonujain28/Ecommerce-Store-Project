from django.contrib import admin
from .models import (
    Product,
    Order,
    UserPreference,
    CartItem,
    WishlistItem,
    Review,
)

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "stock", "customizable")
    list_filter = ("category", "customizable")
    search_fields = ("name", "description")


# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
    "user",
    "product",
    "rating",
    "review_image",
    "created_at",
)
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "product__name", "comment")


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username",)


admin.site.register(CartItem)
admin.site.register(WishlistItem)
admin.site.register(UserPreference)