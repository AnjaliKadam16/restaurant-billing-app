document.addEventListener("DOMContentLoaded", function () {

    // 🔥 MENU CLICK
    document.querySelectorAll(".menu-item").forEach(button => {
        button.addEventListener("click", function () {
            let name = this.dataset.name;
            let price = parseFloat(this.dataset.price);
            addItem(name, price);
        });
    });

    // 🔥 GENERATE BILL BUTTON
    document.getElementById("generateBtn")
        .addEventListener("click", generateBill);

});

let cart = [];

function addItem(name, price) {
    let item = cart.find(i => i.name === name);

    if (item) {
        item.qty++;
    } else {
        cart.push({ name, price, qty: 1 });
    }

    updateCart();
}

function updateCart() {
    let cartList = document.getElementById("cart");
    cartList.innerHTML = "";

    let subtotal = 0;

    cart.forEach((item, index) => {
        let li = document.createElement("li");

        let totalPrice = (item.qty * item.price).toFixed(2);

        li.innerHTML = `
        <div class="cart-row">
            <span>${item.name} x${item.qty} = ₹${totalPrice}</span>
            <div class="actions">
                <button class="small-btn" data-action="inc" data-index="${index}">+</button>
                <button class="small-btn" data-action="dec" data-index="${index}">−</button>
                <button class="delete-btn" data-action="del" data-index="${index}">✕</button>
            </div>
        </div>
        `;

        cartList.appendChild(li);

        subtotal += item.qty * item.price;
    });

    // Event delegation (clean way)
    cartList.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("click", handleCartAction);
    });

    let gst = subtotal * 0.05;
    let total = subtotal + gst;

    document.getElementById("subtotal").textContent = subtotal.toFixed(2);
    document.getElementById("gst").textContent = gst.toFixed(2);
    document.getElementById("total").textContent = total.toFixed(2);
}

function handleCartAction(e) {
    let index = e.target.dataset.index;
    let action = e.target.dataset.action;

    if (action === "inc") cart[index].qty++;
    if (action === "dec") {
        if (cart[index].qty > 1) cart[index].qty--;
        else cart.splice(index, 1);
    }
    if (action === "del") cart.splice(index, 1);

    updateCart();
}

function generateBill() {
    let phone = document.getElementById("phone").value.trim();
    let payment = document.getElementById("payment").value;

    let subtotal = parseFloat(document.getElementById("subtotal").textContent);
    let gst = parseFloat(document.getElementById("gst").textContent);
    let total = parseFloat(document.getElementById("total").textContent);

    if (cart.length === 0) {
        alert("Cart is empty ❌");
        return;
    }
    if(!phone) {
        alert("Enter phone number ❌");
        return;
    }

    // Strong phone validation
    let phoneRegex = /^\+\d{10,15}$/;
    if (!phoneRegex.test(phone)) {
        alert("Enter valid phone (+91XXXXXXXXXX) ❌");
        return;
    }

    let btn = document.getElementById("generateBtn");
    btn.disabled = true;
    btn.textContent = "Processing...";

    fetch('/save_order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            phone,
            subtotal,
            gst,
            total,
            payment,
            items: cart
        })
    })
    .then(res => {
        if (!res.ok) throw new Error("Server error");
        return res.json();
    })
    .then(data => {
        window.location.href = data.invoice_url;

        cart = [];
        updateCart();
    })
    .catch(err => {
        console.error(err);
        alert("Something went wrong ❌");
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = "Generate Bill";
    });
}