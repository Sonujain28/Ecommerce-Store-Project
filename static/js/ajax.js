// ==========================
// CSRF TOKEN
// ==========================
function getCSRFToken() {
    let token = document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];

    if (!token) {
        console.error("❌ CSRF Token not found!");
    }

    return token;
}


// ==========================
// COMMON FETCH HANDLER
// ==========================
function handleResponse(res) {
    if (!res.ok) {
        throw new Error("Server Error: " + res.status);
    }
    return res.json();
}


// ==========================
// ADD TO WISHLIST
// ==========================
function addToWishlist(productId){
    fetch(`/add_to_wishlist/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
    .then(handleResponse)
    .then(data => {
        alert(data.message);
    })
    .catch(err => {
        console.error("❌ Wishlist Error:", err);
        alert("Something went wrong!");
    });
}


// ==========================
// ADD TO CART
// ==========================
function addToCart(productId){
    fetch(`/add_to_cart/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin',
        body: JSON.stringify({
            quantity: 1
        })
    })
    .then(handleResponse)
    .then(data => {
        alert(data.message);
    })
    .catch(err => {
        console.error("❌ Cart Error:", err);
        alert("Cart failed! Maybe login required or server error.");
    });
}


// ==========================
// REMOVE FROM WISHLIST
// ==========================
function removeFromWishlist(productId){
    fetch(`/remove_from_wishlist/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
    .then(handleResponse)
    .then(data => {
        alert(data.message);
        location.reload();
    })
    .catch(err => {
        console.error("❌ Remove Error:", err);
        alert("Remove failed!");
    });
}


// ==========================
// FILTER + SORT AJAX
// ==========================
document.addEventListener("DOMContentLoaded", function(){

    const category = document.getElementById("categoryFilter");
    const sort = document.getElementById("sortFilter");

    if(category){
        category.addEventListener("change", function(e){
            e.preventDefault();
            loadProducts();
        });
    }

    if(sort){
        sort.addEventListener("change", function(e){
            e.preventDefault();
            loadProducts();
        });
    }

});


// ==========================
// LOAD PRODUCTS (AJAX)
// ==========================
function loadProducts(){

    let category = document.getElementById("categoryFilter")?.value || "";
    let sort = document.getElementById("sortFilter")?.value || "";

    fetch(`/filter_products/?category=${category}&sort=${sort}`)
    .then(res => {
        if (!res.ok) throw new Error("Filter error");
        return res.text();
    })
    .then(html => {
        document.getElementById("productContainer").innerHTML = html;
    })
    .catch(err => {
        console.error("❌ Filter Error:", err);
    });
}