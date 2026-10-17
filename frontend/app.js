const API_URL = "http://127.0.0.1:8000";

// ---------- Состояние ----------
let currentUser = null;
let accessToken = localStorage.getItem("access_token");
let refreshToken = localStorage.getItem("refresh_token");
let allCategories = [];
let allProducts = [];

// ---------- DOM ----------
const productsContainer = document.getElementById("products");
const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const userInfo = document.getElementById("user-info");
const authMessage = document.getElementById("auth-message");
const logoutButton = document.getElementById("logout-button");
const adminLink = document.getElementById("admin-link");
const menuTitle = document.getElementById("menu-title");
const menuView = document.getElementById("menu-view");
const ordersView = document.getElementById("my-orders");
const ordersList = document.getElementById("orders-list");

const menuButton = document.getElementById("menu-button");
const myOrdersButton = document.getElementById("my-orders-button");
const backToMenuButton = document.getElementById("back-to-menu");

// ---------- HTTP ----------
async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = data?.detail || `Ошибка API: ${response.status}`;
    throw new Error(
      typeof message === "string" ? message : JSON.stringify(message),
    );
  }

  return data;
}

// ---------- Токены ----------
function saveTokens(tokens) {
  accessToken = tokens.access_token;
  refreshToken = tokens.refresh_token;
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
}

function clearTokens() {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

async function refreshAccessToken() {
  if (!refreshToken) return false;

  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    clearTokens();
    return false;
  }
  saveTokens(data);
  return true;
}

// ---------- Auth UI ----------
function renderAuthState() {
  const isLoggedIn = currentUser !== null;
  loginForm.hidden = isLoggedIn;
  logoutButton.hidden = !isLoggedIn;
  adminLink.hidden = currentUser?.role !== "admin";

  userInfo.textContent = isLoggedIn
    ? `Вы вошли как ${currentUser.name} (${currentUser.role})`
    : "Вы не вошли в аккаунт";
}

async function loadCurrentUser() {
  currentUser = await apiRequest("/users/me");
  renderAuthState();
}

// ---------- Навигация между экранами ----------
function showMenuView() {
  if (menuView) menuView.hidden = false;
  if (ordersView) ordersView.hidden = true;
  menuButton?.setAttribute("aria-current", "page");
  myOrdersButton?.removeAttribute("aria-current");
}

function showOrdersView() {
  if (menuView) menuView.hidden = true;
  if (ordersView) ordersView.hidden = false;
  myOrdersButton?.setAttribute("aria-current", "page");
  menuButton?.removeAttribute("aria-current");
}

menuButton?.addEventListener("click", showMenuView);

myOrdersButton?.addEventListener("click", async () => {
  if (!accessToken) {
    alert("Сначала войдите в аккаунт.");
    return;
  }
  showOrdersView();
  await loadMyOrders();
});

backToMenuButton?.addEventListener("click", showMenuView);

adminLink?.addEventListener("click", () => {
  window.location.href = "admin.html";
});

// ---------- Меню ----------
async function loadMenu() {
  try {
    const [categories, products] = await Promise.all([
      apiRequest("/categories/"),
      apiRequest("/products"),
    ]);

    allCategories = categories;
    allProducts = products;

    // Сообщаем cart.js, что товары готовы
    window.dispatchEvent(
      new CustomEvent("products:loaded", { detail: allProducts }),
    );

    renderCategories();
  } catch (error) {
    console.error("Не удалось загрузить меню:", error);
    productsContainer.textContent =
      "Не удалось загрузить меню. Проверьте backend.";
  }
}

function renderCategories() {
  if (menuTitle) menuTitle.textContent = "Наше меню";

  productsContainer.replaceChildren();
  productsContainer.replaceChildren();

  if (!allCategories.length) {
    productsContainer.textContent = "Категорий пока нет.";
    return;
  }

  for (const category of allCategories) {
    const card = document.createElement("article");
    card.className = "product-card category-card";

    if (category.image_url) {
      const img = document.createElement("img");
      img.src = category.image_url;
      img.alt = category.name;
      img.className = "category-image";
      card.append(img);
    }

    const title = document.createElement("h3");
    title.textContent = category.name;

    const description = document.createElement("p");
    description.textContent = category.description || "Посмотреть блюда";

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "Открыть категорию";
    button.addEventListener("click", () => renderCategoryProducts(category));

    card.append(title, description, button);
    productsContainer.append(card);
  }
}

function renderCategoryProducts(category) {
  // Меняем заголовок на название категории
  if (menuTitle) menuTitle.textContent = category.name;

  productsContainer.replaceChildren();

  // НЕ создаём больше <h3> с названием — оно уже в заголовке
  const backButton = document.createElement("button");
  backButton.type = "button";
  backButton.textContent = "← Все категории";
  backButton.addEventListener("click", renderCategories);

  productsContainer.append(backButton);

  const categoryProducts = allProducts.filter(
    (p) => p.category_id === category.id && p.is_active,
  );

  if (!categoryProducts.length) {
    const msg = document.createElement("p");
    msg.textContent = "В этой категории пока нет блюд.";
    productsContainer.append(msg);
    return;
  }

  for (const product of categoryProducts) {
    const card = document.createElement("article");
    card.className = "product-card";

    const title = document.createElement("h3");
    title.textContent = product.name;

    const price = document.createElement("p");
    price.className = "product-price";
    price.textContent = `${product.price} ₽`;

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "В корзину";
    button.dataset.addToCart = product.id;

    card.append(title, price, button);
    productsContainer.append(card);
  }
}

// ---------- Мои заказы ----------
async function loadMyOrders() {
  ordersList.replaceChildren();
  ordersList.textContent = "Загружаем заказы...";

  try {
    const orders = await apiRequest("/orders");

    ordersList.replaceChildren();

    if (!orders.length) {
      ordersList.textContent = "У вас пока нет заказов.";
      return;
    }

    for (const order of orders) {
      const card = document.createElement("article");
      card.className = "order-card";

      const header = document.createElement("header");
      header.className = "order-card-header";

      const title = document.createElement("h3");
      title.textContent = `Заказ №${order.id}`;

      const status = document.createElement("span");
      status.className = `order-status order-status--${order.status ?? "pending"}`;
      status.textContent = statusLabel(order.status);

      header.append(title, status);

      const meta = document.createElement("p");
      meta.className = "order-meta";
      meta.textContent = order.created_at
        ? new Date(order.created_at).toLocaleString("ru-RU")
        : "";

      const itemsList = document.createElement("ul");
      itemsList.className = "order-items";

      for (const item of order.items ?? []) {
        const li = document.createElement("li");
        const name =
          item.name ?? item.product?.name ?? `Товар #${item.product_id}`;
        li.innerHTML = `
          <span class="order-item-name">${escapeHtml(name)}</span>
          <span class="order-item-qty">${item.quantity} × ${item.unit_price} ₽</span>
        `;
        itemsList.append(li);
      }

      const footer = document.createElement("footer");
      footer.className = "order-card-footer";

      const total = document.createElement("strong");
      total.textContent = `Итого: ${order.total} ₽`;

      footer.append(total);

      card.append(header, meta, itemsList, footer);
      ordersList.append(card);
    }
  } catch (error) {
    ordersList.replaceChildren();
    const msg = document.createElement("p");
    msg.textContent = `Не удалось загрузить заказы: ${error.message}`;
    ordersList.append(msg);
  }
}

// Человекочитаемый статус
function statusLabel(status) {
  const map = {
    pending: "Ожидает",
    confirmed: "Подтверждён",
    completed: "Выполнен",
    cancelled: "Отменён",
  };
  return map[status] ?? status ?? "—";
}

// Экранирование HTML
function escapeHtml(value) {
  return String(value).replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        char
      ],
  );
}

// ---------- Логин / логаут ----------
loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  authMessage.textContent = "";

  const submitButton = loginForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;

  try {
    const formData = new URLSearchParams();
    formData.set("username", emailInput.value.trim());
    formData.set("password", passwordInput.value);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });

    const tokens = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(tokens?.detail || "Не удалось войти в аккаунт");
    }

    saveTokens(tokens);
    await loadCurrentUser();

    passwordInput.value = "";
    authMessage.textContent = "Вход выполнен успешно.";
  } catch (error) {
    console.error("Ошибка входа:", error);
    currentUser = null;
    clearTokens();
    renderAuthState();
    authMessage.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

logoutButton.addEventListener("click", async () => {
  const oldRefresh = refreshToken;
  currentUser = null;
  clearTokens();
  renderAuthState();
  authMessage.textContent = "Вы вышли из аккаунта.";

  if (oldRefresh) {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: oldRefresh }),
      });
    } catch (error) {
      console.error("Не удалось отозвать refresh-токен:", error);
    }
  }
});

// ---------- Инициализация ----------
async function initialize() {
  if (accessToken) {
    try {
      await loadCurrentUser();
      return;
    } catch (error) {
      console.warn("Access-токен не подошёл:", error);
    }
  }

  if (refreshToken) {
    try {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        await loadCurrentUser();
        return;
      }
    } catch (error) {
      console.error("Не удалось обновить токен:", error);
    }
  }

  currentUser = null;
  clearTokens();
  renderAuthState();
}

renderAuthState();
showMenuView();
loadMenu();
initialize();
