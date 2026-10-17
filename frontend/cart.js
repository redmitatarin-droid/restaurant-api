const CART_KEY = "rusnas_cart";
const MAX_QUANTITY = 20;

// ---------- Состояние ----------
let cart = readCart();
let cartProducts = [];

// ---------- localStorage ----------
function readCart() {
  try {
    const saved = JSON.parse(localStorage.getItem(CART_KEY) || "[]");
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [];
  }
}

function saveCart() {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
}

// ---------- Хелперы ----------
function getProduct(productId) {
  return cartProducts.find((p) => Number(p.id) === Number(productId));
}

function cartQuantity() {
  return cart.reduce((sum, item) => sum + item.quantity, 0);
}

function cartTotal() {
  return cart.reduce((sum, item) => {
    const product = getProduct(item.product_id);
    return sum + (product ? product.price * item.quantity : 0);
  }, 0);
}

// ---------- Действия ----------
function addToCart(productId) {
  const product = getProduct(productId);

  if (!product) {
    alert("Товар не найден. Обновите страницу.");
    return;
  }
  if (!product.is_active) {
    alert("Это блюдо сейчас недоступно.");
    return;
  }

  const existing = cart.find(
    (item) => Number(item.product_id) === Number(productId),
  );

  if (existing) {
    if (existing.quantity >= MAX_QUANTITY) {
      alert(`Максимум ${MAX_QUANTITY} штук одного блюда.`);
      return;
    }
    existing.quantity += 1;
  } else {
    cart.push({ product_id: Number(productId), quantity: 1 });
  }

  saveCart();
  renderCart();
}

function changeQuantity(productId, delta) {
  const item = cart.find((i) => Number(i.product_id) === Number(productId));
  if (!item) return;

  const next = item.quantity + delta;

  if (next <= 0) {
    cart = cart.filter((i) => Number(i.product_id) !== Number(productId));
  } else if (next > MAX_QUANTITY) {
    alert(`Максимум ${MAX_QUANTITY} штук одного блюда.`);
    return;
  } else {
    item.quantity = next;
  }

  saveCart();
  renderCart();
}

function removeFromCart(productId) {
  cart = cart.filter((i) => Number(i.product_id) !== Number(productId));
  saveCart();
  renderCart();
}

// ---------- Рендер ----------
function renderCart() {
  const container = document.getElementById("cart-items");
  const totalElement = document.getElementById("cart-total");
  const countElement = document.getElementById("cart-count");

  if (!container || !totalElement || !countElement) return;

  countElement.textContent = cartQuantity();
  totalElement.textContent = `${cartTotal()} ₽`;
  container.replaceChildren();

  if (!cart.length) {
    container.textContent = "Корзина пока пуста.";
    return;
  }

  for (const item of cart) {
    const product = getProduct(item.product_id);
    const row = document.createElement("article");
    row.className = "cart-item";

    if (!product) {
      row.textContent = `Товар #${item.product_id} больше недоступен.`;
      container.append(row);
      continue;
    }

    const name = document.createElement("h4");
    name.textContent = product.name;

    const price = document.createElement("p");
    price.textContent = `${product.price} ₽ за штуку`;

    const controls = document.createElement("div");
    controls.className = "cart-controls";

    const minus = document.createElement("button");
    minus.type = "button";
    minus.textContent = "−";
    minus.setAttribute("aria-label", `Уменьшить: ${product.name}`);
    minus.addEventListener("click", () => changeQuantity(product.id, -1));

    const quantity = document.createElement("span");
    quantity.textContent = item.quantity;

    const plus = document.createElement("button");
    plus.type = "button";
    plus.textContent = "+";
    plus.setAttribute("aria-label", `Увеличить: ${product.name}`);
    plus.addEventListener("click", () => changeQuantity(product.id, 1));

    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "Удалить";
    remove.addEventListener("click", () => removeFromCart(product.id));

    controls.append(minus, quantity, plus, remove);
    row.append(name, price, controls);
    container.append(row);
  }
}

// ---------- Оформление ----------
async function checkout() {
  const message = document.getElementById("checkout-message");
  const button = document.getElementById("checkout-button");

  if (!cart.length) {
    message.textContent = "Добавь хотя бы одно блюдо.";
    return;
  }
  if (!localStorage.getItem("access_token")) {
    message.textContent = "Сначала войди в аккаунт.";
    return;
  }

  button.disabled = true;
  message.textContent = "Оформляем заказ...";

  try {
    const result = await apiRequest("/orders", {
      method: "POST",
      body: JSON.stringify({
        items: cart.map((i) => ({
          product_id: i.product_id,
          quantity: i.quantity,
        })),
      }),
    });

    cart = [];
    saveCart();
    renderCart();

    message.textContent = `Заказ №${result.id} оформлен! Сумма: ${result.total} ₽.`;
  } catch (error) {
    message.textContent = `Не удалось оформить заказ: ${error.message}`;
  } finally {
    button.disabled = false;
  }
}

// ---------- Слушатели ----------
document.getElementById("products")?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-add-to-cart]");
  if (!button) return;

  const productId = Number(button.dataset.addToCart);
  addToCart(productId);
});

document.getElementById("checkout-button")?.addEventListener("click", checkout);

// Ждём, когда app.js загрузит товары
window.addEventListener("products:loaded", (event) => {
  cartProducts = event.detail ?? [];
  renderCart();
});

// Если товары уже загружены — берём сразу
if (window.allProducts?.length) {
  cartProducts = window.allProducts;
  renderCart();
} else {
  renderCart();
}
