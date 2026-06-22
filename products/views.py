from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, CartItem, WishlistItem, UserPreference, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
import json
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum
import random
from django.template.loader import render_to_string
# Make sure openai is installed: pip install openai
@login_required
def add_review(request, product_id):

    print("REVIEW FUNCTION CALLED")

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":

        print("POST RECEIVED")

        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment")
        review_image = request.FILES.get("review_image")
        print(rating)
        print(comment)

        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                "rating": rating,
                "comment": comment,
                "review_image": review_image,
            }
        )

        print("REVIEW SAVED")

    return redirect("product_detail", id=product.id)

# ----------------------
# SIGNUP PAGE
# ----------------------
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Login immediately
            merge_guest_data(request, user)  # Merge guest cart/wishlist
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


# ----------------------
# HOME PAGE
# ----------------------


def home(request):
    category_name = request.GET.get("category")
    sort = request.GET.get("sort")
    query = request.GET.get("q")  # 🔥 Search query

    products = Product.objects.all()
    # 🎯 QUIZ FILTERING
    skin = request.GET.get("skin")
    fashion = request.GET.get("fashion")
    class_type = request.GET.get("class")
    # 🔍 SEARCH FILTER - Search in both name and description
    if query:
        products = (
            products.filter(Q(name__icontains=query) | Q(description__icontains=query))
            .exclude(name__isnull=True)
            .exclude(name="")
        )

    # 📂 CATEGORY FILTER
    if category_name and category_name != "None":
        products = products.filter(category=category_name)

    # 💰 SORTING
    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")

    recommended = None
    if request.user.is_authenticated:
        try:
            pref = UserPreference.objects.get(user=request.user)
            preferred_categories = pref.preference.split(",")
            recommended = Product.objects.filter(
                category__in=preferred_categories
            ).exclude(id__in=[p.id for p in products])[:4]
        except UserPreference.DoesNotExist:
            recommended = None

    categories = [
        choice[0] for choice in Product.CATEGORY_CHOICES if choice[0] is not None
    ]

    return render(
        request,
        "products/home.html",
        {
            "products": products,
            "recommended": recommended,
            "categories": categories,
            "selected_category": category_name,
            "search_query": query,
            "show_header": True,
        },
    )


def category_products(request, category_name, subcategory_name):

    if category_name.lower() == "skin":
        products = Product.objects.filter(skin_type__iexact=subcategory_name)

    elif category_name.lower() == "fashion":
        products = Product.objects.filter(fashion_type__iexact=subcategory_name)

    elif category_name.lower() == "class":
        products = Product.objects.filter(class_type__iexact=subcategory_name)

    # ✅ NEW: COLLECTION FILTER (wedding, genz, etc.)
    elif category_name.lower() == "collection":
        products = Product.objects.filter(collection__iexact=subcategory_name)

    else:
        products = Product.objects.none()

    return render(
        request,
        "products/category_products.html",
        {
            "products": products,
            "category_name": category_name,
            "subcategory_name": subcategory_name,
            "show_header": True,
        },
    )


# ----------------------
# PRODUCT DETAIL PAGE
# ----------------------
from .models import Review
from django.db.models import Avg


def product_detail(request, id):

    product = get_object_or_404(Product, id=id)

    reviews = product.reviews.all().order_by("-created_at")

    average_rating = (
        reviews.aggregate(avg=Avg("rating"))["avg"] or 0
    )

    recommended = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "recommended": recommended,
            "reviews": reviews,
            "average_rating": round(average_rating, 1),
            "show_header": True,
        },
    )


# ----------------------
# ADD TO CART (guest & logged-in)
# ----------------------
def add_to_cart(request, product_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            quantity = int(data.get("quantity", 1))
        except:
            quantity = 1  # fallback

        product = Product.objects.get(id=product_id)

        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user, product=product
            )
        else:
            if not request.session.session_key:
                request.session.create()

            cart_item, created = CartItem.objects.get_or_create(
                session_key=request.session.session_key, product=product
            )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        return JsonResponse(
            {"status": "success", "message": "🛒 Product added to cart!"}
        )


# ----------------------
# CART PAGE
# ----------------------
def cart_view(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart_items = CartItem.objects.filter(session_key=request.session.session_key)

    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(
        request, "products/cart.html", {"cart_items": cart_items, "total": total}
    )


# ----------------------
# REMOVE FROM CART
# ----------------------
def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user, product_id=product_id).delete()
    else:
        if request.session.session_key:
            CartItem.objects.filter(
                session_key=request.session.session_key, product_id=product_id
            ).delete()
    return redirect("cart")


# ----------------------
# INCREASE QUANTITY
# ----------------------
def increase_quantity(request, product_id):
    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(
            user=request.user, product_id=product_id
        ).first()
    else:
        cart_item = CartItem.objects.filter(
            session_key=request.session.session_key, product_id=product_id
        ).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


# ----------------------
# DECREASE QUANTITY
# ----------------------
def decrease_quantity(request, product_id):
    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(
            user=request.user, product_id=product_id
        ).first()
    else:
        cart_item = CartItem.objects.filter(
            session_key=request.session.session_key, product_id=product_id
        ).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect("cart")


# ----------------------
# ADD TO WISHLIST
# ----------------------
def add_to_wishlist(request, product_id):

    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        if not request.session.session_key:
            request.session.create()

        wishlist = request.session.get("wishlist", [])

        if product_id not in wishlist:
            wishlist.append(product_id)
            request.session["wishlist"] = wishlist

        return JsonResponse({"status": "success", "message": "❤️ Added to wishlist!"})


# ----------------------
# VIEW WISHLIST
# ----------------------
def wishlist_view(request):
    # Get wishlist items from session
    wishlist_ids = request.session.get("wishlist", [])
    wishlist_items = Product.objects.filter(id__in=wishlist_ids).distinct()

    return render(request, "products/wishlist.html", {"wishlist_items": wishlist_items})


# ----------------------
# REMOVE FROM WISHLIST
# ----------------------
def remove_from_wishlist(request, product_id):

    if request.method == "POST":
        wishlist = request.session.get("wishlist", [])

        if product_id in wishlist:
            wishlist.remove(product_id)
            request.session["wishlist"] = wishlist

        return JsonResponse(
            {"status": "success", "message": "❌ Removed from wishlist"}
        )


# ----------------------
# CHECKOUT PAGE
# ----------------------
@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items:
        return redirect("cart")

    total = sum(item.product.price * item.quantity for item in cart_items)

    # Create Order
    order = Order.objects.create(user=request.user, total_amount=total)

    # Create Order Items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )

    # Clear Cart
    cart_items.delete()

    return render(request, "products/order_success.html", {"order": order})


# ----------------------
# HELPER: Merge guest cart/wishlist after login/signup
# ----------------------
def merge_guest_data(request, user):
    session_key = request.session.session_key
    if session_key:
        # Merge cart
        guest_cart = CartItem.objects.filter(session_key=session_key)
        for item in guest_cart:
            cart_item, created = CartItem.objects.get_or_create(
                user=user, product=item.product
            )
            if not created:
                cart_item.quantity += item.quantity
            else:
                cart_item.quantity = item.quantity
            cart_item.save()
        guest_cart.delete()

        # Merge wishlist
        wishlist_ids = request.session.get("wishlist", [])
        for pid in wishlist_ids:
            product = Product.objects.filter(id=pid).first()
            if product:
                WishlistItem.objects.get_or_create(user=user, product=product)
        if "wishlist" in request.session:
            del request.session["wishlist"]


# ----------------------
# SMART RECOMMENDATIONS (AI-Like)
# ----------------------


def ai_chat(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "response": "Hi 💕 I am your shopping assistant. What are you looking for?"
            }
        )

    data = json.loads(request.body)
    message = data.get("message", "").strip().lower()

    # ===============================
    # GREETING ENGINE
    # ===============================

    greetings = ["hi", "hello", "hey", "hii"]

    if message in greetings:
        reply = random.choice(
            [
                "Hi beautiful 💖 Looking for skincare, makeup or fashion?",
                "Hey ✨ I can help you find perfect products.",
                "Hello 🌸 Tell me your style!",
            ]
        )
        return JsonResponse({"response": reply})

    # ===============================
    # CATEGORY INTELLIGENCE ENGINE
    # ===============================

    categories_map = {
        # 🔹 SKINCARE
        "skincare": "Skincare",
        "skin": "Skincare",
        "facewash": "Skincare",
        "cleanser": "Skincare",
        "moisturizer": "Skincare",
        "cream": "Skincare",
        "serum": "Skincare",
        "toner": "Skincare",
        "sunscreen": "Skincare",
        "spf": "Skincare",
        "lotion": "Skincare",
        "mask": "Skincare",
        "scrub": "Skincare",
        "gel": "Skincare",
        # 🔹 MAKEUP
        "makeup": "Makeup",
        "lipstick": "Makeup",
        "lip": "Makeup",
        "gloss": "Makeup",
        "foundation": "Makeup",
        "compact": "Makeup",
        "concealer": "Makeup",
        "blush": "Makeup",
        "eyeliner": "Makeup",
        "kajal": "Makeup",
        "mascara": "Makeup",
        "highlighter": "Makeup",
        "palette": "Makeup",
        "nailpaint": "Makeup",
        "cosmetic": "Makeup",
        # 🔹 CLOTHING
        "dress": "Clothing",
        "fashion": "Clothing",
        "outfit": "Clothing",
        "top": "Clothing",
        "jeans": "Clothing",
        "shirt": "Clothing",
        "tshirt": "Clothing",
        "kurti": "Clothing",
        "saree": "Clothing",
        "lehenga": "Clothing",
        "jacket": "Clothing",
        "coat": "Clothing",
        "pant": "Clothing",
        "shorts": "Clothing",
        "skirt": "Clothing",
        # 🔹 ACCESSORIES
        "accessories": "Accessories",
        "bag": "Accessories",
        "handbag": "Accessories",
        "wallet": "Accessories",
        "belt": "Accessories",
        "jewellery": "Accessories",
        "necklace": "Accessories",
        "ring": "Accessories",
        "earring": "Accessories",
        "bracelet": "Accessories",
        "watch": "Accessories",
        "sunglasses": "Accessories",
    }

    for keyword, category_name in categories_map.items():
        if keyword in message:
            products = Product.objects.filter(category__iexact=category_name)[:4]

            if products.exists():
                return JsonResponse(
                    {
                        "response": f"I found some {category_name} products 💕",
                        "products": [
                            {
                                "name": p.name,
                                "price": p.price,
                                "image": p.image.url if p.image else "",
                                "url": f"/product/{p.id}/",
                            }
                            for p in products
                        ],
                    }
                )

    # ===============================
    # STYLE INTELLIGENCE ENGINE
    # ===============================

    style_keywords = ["luxury", "minimal", "bold", "elegant", "modern"]

    for style in style_keywords:
        if style in message:
            products = Product.objects.filter(class_type__icontains=style)[:4]

            if products.exists():
                return JsonResponse(
                    {
                        "response": f"I found some {style} style products 💕",
                        "products": [
                            {
                                "name": p.name,
                                "price": p.price,
                                "image": p.image.url if p.image else "",
                                "url": f"/product/{p.id}/",
                            }
                            for p in products
                        ],
                    }
                )

    # ===============================
    # 🔥 SMART PRODUCT NAME SEARCH (WORD BASED)
    # ===============================

    words = message.split()  # "titan watch" -> ["titan", "watch"]

    query = Q()

    for word in words:
        query |= Q(name__icontains=word)
        query |= Q(description__icontains=word)
        query |= Q(category__icontains=word)
        query |= Q(class_type__icontains=word)

    products = Product.objects.filter(query).distinct()[:4]

    if products.exists():
        return JsonResponse(
            {
                "response": f"I found some products related to '{message}' 💕",
                "products": [
                    {
                        "name": p.name,
                        "price": p.price,
                        "image": p.image.url if p.image else "",
                        "url": f"/product/{p.id}/",
                    }
                    for p in products
                ],
            }
        )

    # ===============================
    # GENERAL RESPONSE
    # ===============================

    reply = random.choice(
        [
            "Tell me your skin type or fashion style 💕",
            "Try typing like: 'makeup', 'skincare', 'dress' ✨",
            "Looking for something special today? 🌸",
        ]
    )

    return JsonResponse({"response": reply})


# ----------------------
# ALL PRODUCTS PAGE
# ----------------------
def all_products(request):
    products = Product.objects.all()

    category_name = request.GET.get("category")
    sort = request.GET.get("sort")
    query = request.GET.get("q")

    # 🔍 SEARCH
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # 📂 CATEGORY FILTER
    if category_name and category_name != "None":
        products = products.filter(category=category_name)

    # 💰 SORTING
    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")

    categories = [
        choice[0] for choice in Product.CATEGORY_CHOICES if choice[0] is not None
    ]

    return render(
        request,
        "products/all_products.html",
        {
            "products": products,
            "categories": categories,
            "selected_category": category_name,
            "search_query": query,
            "show_header": True,
        },
    )


def filter_products(request):
    products = Product.objects.all()

    category = request.GET.get("category")
    sort = request.GET.get("sort")

    if category and category != "None":
        products = products.filter(category=category)

    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")

    html = render_to_string(
        "products/product_list.html", {"products": products}, request=request
    )

    return HttpResponse(html)


@login_required
def my_orders(request):

    query = request.GET.get("q", "")

    orders = Order.objects.filter(user=request.user)

    # ✅ Order search (product name search inside order items)
    if query:
        orders = orders.filter(items__product__name__icontains=query).distinct()

    orders = orders.order_by("-created_at")

    return render(
        request,
        "products/my_orders.html",
        {"orders": orders, "search_query": query, "show_header": False},
    )


def gift_card(request):
    return render(request, "products/gift_card.html")

@staff_member_required
def admin_dashboard(request):

    total_orders = Order.objects.count()

    total_revenue = (
        Order.objects.aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    total_users = User.objects.count()

    total_products = Product.objects.count()

    total_reviews = Review.objects.count()

    context = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_users": total_users,
        "total_products": total_products,
        "total_reviews": total_reviews,
    }

    return render(
        request,
        "products/admin_dashboard.html",
        context
    )