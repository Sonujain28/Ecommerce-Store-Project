document.addEventListener('DOMContentLoaded', () => {

    const btn = document.getElementById('ai-chat-btn');
    const win = document.getElementById('ai-chat-window');
    const send = document.getElementById('ai-send');
    const input = document.getElementById('ai-input');
    const msgs = document.getElementById('ai-messages');

    btn.addEventListener('click', () => {
        win.style.display =
            win.style.display === 'block' ? 'none' : 'block';
    });

    function append(role, text) {
        const div = document.createElement('div');

        div.style.margin = "8px 0";

        if (role === "user") {
            div.style.textAlign = "right";
            div.innerHTML =
                `<span style="background:#ff1a8c;
                color:white;
                padding:6px 12px;
                border-radius:12px;">
                ${text}
                </span>`;
        }
        else {
            div.innerHTML =
                `<span style="background:#f3f3f3;
                padding:8px 12px;
                border-radius:12px;
                display:inline-block;">
                ${text}
                </span>`;
        }

        msgs.appendChild(div);
        msgs.scrollTop = msgs.scrollHeight;
        return div;
    }

    async function sendMessage() {

        const text = input.value.trim();
        if (!text) return;

        append("user", text);
        input.value = "";

        const botNode = append("bot", "Thinking...");

        const res = await fetch("/ai-chat/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ message: text })
        });

        if (!res.ok) {
            botNode.innerHTML = "Server error ❌";
            return;
        }
        const data = await res.json();
        botNode.innerHTML = "";

if (data.products && data.products.length > 0) {

    data.products.forEach(product => {

    const card = `
<div class="chat-product-card">
    <img src="${product.image}" alt="${product.name}">
    <div class="chat-product-info">
        <h6>${product.name}</h6>
        <p class="price">₹${product.price}</p>
        <a href="${product.url}" class="view-btn">
            View Product
        </a>
    </div>
</div>
`;
        botNode.innerHTML += card;
    });

} else {
    botNode.innerHTML = data.response;
}
    }

    send.addEventListener("click", sendMessage);

    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const c = cookies[i].trim();
                if (c.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(
                        c.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return cookieValue;
    }

});
