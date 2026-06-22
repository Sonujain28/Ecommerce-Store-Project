from django.urls import path
from django.contrib.auth import views as auth_views
from users import views as user_views
from products import views as product_views

urlpatterns = [
    path(
    "review/<int:product_id>/",
    product_views.add_review,
    name="add_review",
),
    # ----------------------
    # AUTHENTICATION
    # ----------------------
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(template_name="registration/logout.html"),
        name="logout",
    ),
    path("accounts/signup/", user_views.signup, name="signup"),
    # ----------------------
    # HOME & PRODUCTS
    # ----------------------
    path("", product_views.home, name="home"),
    path(
        "category/<str:category_name>/<str:subcategory_name>/",
        product_views.category_products,
        name="category_products",
    ),
    path("product/<int:id>/", product_views.product_detail, name="product_detail"),
    path("products/", product_views.all_products, name="all_products"),
    path("filter_products/", product_views.filter_products, name="filter_products"),
    # ----------------------
    # CART
    # ----------------------
    path("cart/", product_views.cart_view, name="cart"),
    path(
        "add_to_cart/<int:product_id>/", product_views.add_to_cart, name="add_to_cart"
    ),
    path(
        "remove_from_cart/<int:product_id>/",
        product_views.remove_from_cart,
        name="remove_from_cart",
    ),
    path(
        "cart/increase/<int:product_id>/",
        product_views.increase_quantity,
        name="increase_quantity",
    ),
    path(
        "cart/decrease/<int:product_id>/",
        product_views.decrease_quantity,
        name="decrease_quantity",
    ),
    # ----------------------
    # WISHLIST
    # ----------------------
    path("wishlist/", product_views.wishlist_view, name="wishlist"),
    path(
        "add_to_wishlist/<int:product_id>/",
        product_views.add_to_wishlist,
        name="add_to_wishlist",
    ),
    path(
        "remove_from_wishlist/<int:product_id>/",
        product_views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    # ----------------------
    # CHECKOUT
    # ----------------------
    path("checkout/", product_views.checkout_view, name="checkout"),
    path("ai-chat/", product_views.ai_chat, name="ai_chat"),
    # ----------------------
    # MY ORDERS
    # ----------------------
    path("my-orders/", product_views.my_orders, name="my_orders"),
    # ----------------------
    # GIFT CARD
    # ----------------------
    path("gift-card/", product_views.gift_card, name="gift_card"),

    # ----------------------
    # ADMIN DASHBOARD
    # ----------------------
    path(
    "admin-dashboard/",
    product_views.admin_dashboard,
    name="admin_dashboard",
),
]
