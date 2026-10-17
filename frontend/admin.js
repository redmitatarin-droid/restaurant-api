const API_URL = "http://127.0.0.1:8000";

const message = document.getElementById("admin-message");
const ordersContainer = document.getElementById("orders-container");
const reloadButton = document.getElementById("reload-orders");

const accessToken = localStorage.getItem("access_token");

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      ...(options.headers || {}),
      ...(options.body ? { "Content-Type": "application/json" } : {}),
    },
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail;
    const errorMessage =
      typeof detail === "string"
        ? detail
        : detail
          ? JSON.stringify(detail)
          : `Ошибка API: ${response.status}`;

    throw new Error(errorMessage);
  }

  return data;
}

function createOrderCard(order) {
  const card = document.createElement("article");
  card.className = "product-card";

  const title = document.createElement("h3");
  title.textContent = `Заказ №${order.id}`;

  const customer = document.createElement("p");
  customer.textContent = `Клиент: ${order.customer.name} (${order.customer.email})`;

  const date = document.createElement("p");
  date.textContent = `Дата: ${new Date(order.created_at).toLocaleString("ru-RU")}`;

  const status = document.createElement("p");
  const statusLabel = document.createElement("label");
  statusLabel.textContent = "Статус заказа: ";

  const statusSelect = document.createElement("select");

  const statuses = [
    { value: "pending", label: "Новый" },
    { value: "confirmed", label: "Подтверждён" },
    { value: "completed", label: "Выполнен" },
    { value: "cancelled", label: "Отменён" },
  ];
  status.textContent = `Статус: ${
    statuses.find((item) => item.value === order.status)?.label ?? order.status
  }`;

  for (const item of statuses) {
    const option = document.createElement("option");
    option.value = item.value;
    option.textContent = item.label;
    statusSelect.append(option);
  }

  statusSelect.value = order.status;

  const saveStatusButton = document.createElement("button");
  saveStatusButton.textContent = "Сохранить статус";

  const statusMessage = document.createElement("p");

  saveStatusButton.addEventListener("click", async () => {
    saveStatusButton.disabled = true;
    statusMessage.textContent = "Сохраняем...";

    try {
      await apiRequest(`/orders/${order.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({
          new_status: statusSelect.value,
        }),
      });

      order.status = statusSelect.value;
      status.textContent = `Статус: ${
        statuses.find((item) => item.value === order.status)?.label ??
        order.status
      }`;

      statusMessage.textContent = "Статус сохранён.";
    } catch (error) {
      statusMessage.textContent = `Ошибка: ${error.message}`;
    } finally {
      saveStatusButton.disabled = false;
    }
  });

  statusLabel.append(statusSelect);

  const total = document.createElement("p");
  total.className = "product-price";
  total.textContent = `Сумма: ${order.total} ₽`;

  const itemsTitle = document.createElement("h4");
  itemsTitle.textContent = "Состав заказа";

  const itemsList = document.createElement("ul");

  for (const item of order.items) {
    const listItem = document.createElement("li");
    listItem.textContent =
      `${item.product_name} × ${item.quantity} — ` +
      `${item.price * item.quantity} ₽`;

    itemsList.append(listItem);
  }

  card.append(
    title,
    customer,
    date,
    status,
    statusLabel,
    saveStatusButton,
    statusMessage,
    total,
    itemsTitle,
    itemsList,
  );

  return card;
}

async function loadOrders() {
  ordersContainer.replaceChildren();
  message.textContent = "Загружаем заказы...";

  try {
    const orders = await apiRequest("/orders/admin");

    if (!Array.isArray(orders)) {
      throw new Error("Сервер вернул неожиданный формат заказов.");
    }

    if (orders.length === 0) {
      message.textContent = "Заказов пока нет.";
      return;
    }

    for (const order of orders) {
      ordersContainer.append(createOrderCard(order));
    }

    message.textContent = `Всего заказов: ${orders.length}`;
  } catch (error) {
    message.textContent = error.message;
    console.error("Ошибка загрузки заказов:", error);
  }
}

async function initializeAdmin() {
  if (!accessToken) {
    message.textContent =
      "Сначала войдите в аккаунт администратора на странице меню.";
    return;
  }

  try {
    const user = await apiRequest("/users/me");

    if (user.role !== "admin") {
      message.textContent = "Доступ запрещён: нужны права администратора.";
      return;
    }

    message.textContent = `Вы вошли как администратор: ${user.name}`;
    reloadButton.hidden = false;

    await loadOrders();
  } catch (error) {
    message.textContent =
      `Не удалось проверить доступ: ${error.message}. ` +
      "Вернитесь в меню и войдите заново.";
  }
}

reloadButton.addEventListener("click", loadOrders);

initializeAdmin();
