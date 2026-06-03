"use strict";

const LS_TOKEN = "autosalon.token";
const LS_ROLE = "autosalon.role";
const LS_FAVS = "autosalon.favorites";

const $ = (id) => document.getElementById(id);

const store = {
  token: () => localStorage.getItem(LS_TOKEN),
  role: () => localStorage.getItem(LS_ROLE),
  setAuth(token, role) {
    localStorage.setItem(LS_TOKEN, token);
    localStorage.setItem(LS_ROLE, role);
  },
  clearAuth() {
    localStorage.removeItem(LS_TOKEN);
    localStorage.removeItem(LS_ROLE);
  },
  favs() {
    try {
      return JSON.parse(localStorage.getItem(LS_FAVS) || "[]");
    } catch {
      return [];
    }
  },
  setFavs(list) {
    localStorage.setItem(LS_FAVS, JSON.stringify(list));
  },
};

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = store.token();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(path, { ...options, headers });
  if (res.status === 204) return null;

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data?.error?.message || `Ошибка ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

function toast(message, kind = "ok") {
  const el = $("toast");
  el.textContent = message;
  el.className = `toast ${kind}`;
  el.hidden = false;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => (el.hidden = true), 2600);
}

function showError(id, message) {
  const el = $(id);
  el.textContent = message;
  el.hidden = false;
}
function hideError(id) {
  $(id).hidden = true;
}

function money(value) {
  return new Intl.NumberFormat("ru-RU").format(value) + " \u20bd";
}

const BODY_LABELS = {
  sedan: "Седан", hatchback: "Хэтчбек", suv: "Внедорожник",
  coupe: "Купе", wagon: "Универсал",
};

function applyRole() {
  const role = store.role();
  const badge = $("role-badge");
  const logout = $("logout-btn");
  const authPanel = $("auth-panel");
  const adminSections = document.querySelectorAll(".admin-only");

  if (role) {
    badge.textContent = role === "admin" ? "менеджер (admin)" : "клиент (guest)";
    badge.className = `badge ${role === "admin" ? "badge-admin" : "badge-guest"}`;
    logout.hidden = false;
    authPanel.hidden = true;
  } else {
    badge.textContent = "не авторизован";
    badge.className = "badge badge-off";
    logout.hidden = true;
    authPanel.hidden = false;
  }
  adminSections.forEach((s) => (s.hidden = role !== "admin"));
}

async function login() {
  hideError("auth-error");
  const username = $("login-username").value.trim();
  const password = $("login-password").value;
  if (!username || !password) {
    showError("auth-error", "Введите логин и пароль");
    return;
  }
  try {
    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    store.setAuth(data.token, data.role);
    applyRole();
    toast(`Вход выполнен: ${data.role}`);
    $("login-password").value = "";
  } catch (e) {
    showError("auth-error", e.message);
  }
}

function logout() {
  store.clearAuth();
  applyRole();
  toast("Сеанс завершён");
}

async function loadCars() {
  const brand = $("filter-brand").value.trim();
  const maxPrice = $("filter-price").value.trim();
  const params = new URLSearchParams();
  if (brand) params.set("brand", brand);
  if (maxPrice) params.set("max_price", maxPrice);
  const qs = params.toString();

  try {
    const cars = await api(`/cars${qs ? "?" + qs : ""}`);
    renderCars(cars);
  } catch (e) {
    toast(e.message, "err");
  }
}

function renderCars(cars) {
  const grid = $("cars-grid");
  grid.innerHTML = "";
  if (!cars.length) {
    grid.innerHTML = `<p class="fav-empty">Ничего не найдено.</p>`;
    return;
  }
  const favs = store.favs();
  const isAdmin = store.role() === "admin";

  cars.forEach((car) => {
    const faved = favs.includes(car.id);
    const card = document.createElement("div");
    card.className = "car-card";
    card.innerHTML = `
      <div class="car-title">${car.brand} ${car.model}</div>
      <div class="car-meta">${car.year} · ${BODY_LABELS[car.body_type] || car.body_type}</div>
      <div class="car-price">${money(car.price)}</div>
      <div class="car-foot">
        <span class="stock ${car.in_stock ? "in" : "out"}">${car.in_stock ? "в наличии" : "под заказ"}</span>
        <span class="actions"></span>
      </div>`;
    const actions = card.querySelector(".actions");

    const favBtn = document.createElement("button");
    favBtn.className = `icon-btn ${faved ? "active" : ""}`;
    favBtn.textContent = faved ? "★ в избранном" : "☆ в избранное";
    favBtn.onclick = () => toggleFav(car.id);
    actions.appendChild(favBtn);

    if (isAdmin) {
      const del = document.createElement("button");
      del.className = "icon-btn del";
      del.textContent = "удалить";
      del.style.marginLeft = "8px";
      del.onclick = () => deleteCar(car.id);
      actions.appendChild(del);
    }
    grid.appendChild(card);
  });
}

async function addCar() {
  hideError("car-error");
  const payload = {
    brand: $("car-brand").value.trim(),
    model: $("car-model").value.trim(),
    year: Number($("car-year").value),
    price: Number($("car-price").value),
    body_type: $("car-body").value,
  };
  try {
    await api("/cars", { method: "POST", body: JSON.stringify(payload) });
    toast("Автомобиль добавлен");
    ["car-brand", "car-model", "car-year", "car-price"].forEach((id) => ($(id).value = ""));
    loadCars();
  } catch (e) {
    showError("car-error", e.message);
  }
}

async function deleteCar(id) {
  try {
    await api(`/cars/${id}`, { method: "DELETE" });
    toast("Автомобиль удалён");
    loadCars();
    renderFavs();
  } catch (e) {
    toast(e.message, "err");
  }
}

async function loadUsers() {
  try {
    const users = await api("/users");
    const body = $("users-body");
    body.innerHTML = "";
    users.forEach((u) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${u.id}</td><td>${u.name}</td><td>${u.email}</td><td>${u.age ?? "—"}</td>`;
      body.appendChild(tr);
    });
    $("users-table").hidden = false;
  } catch (e) {
    toast(e.message, "err");
  }
}

async function addUser() {
  hideError("user-error");
  const ageRaw = $("user-age").value.trim();
  const payload = {
    name: $("user-name").value.trim(),
    email: $("user-email").value.trim(),
  };
  if (ageRaw) payload.age = Number(ageRaw);
  try {
    await api("/users", { method: "POST", body: JSON.stringify(payload) });
    toast("Пользователь создан");
    ["user-name", "user-email", "user-age"].forEach((id) => ($(id).value = ""));
    loadUsers();
  } catch (e) {
    showError("user-error", e.message);
  }
}

function toggleFav(id) {
  let favs = store.favs();
  favs = favs.includes(id) ? favs.filter((x) => x !== id) : [...favs, id];
  store.setFavs(favs);
  loadCars();
  renderFavs();
}

async function renderFavs() {
  const wrap = $("fav-list");
  const favs = store.favs();
  wrap.innerHTML = "";
  if (!favs.length) {
    wrap.innerHTML = `<span class="fav-empty">Список пуст. Добавьте автомобиль из каталога.</span>`;
    return;
  }
  let cars = [];
  try {
    cars = await api("/cars");
  } catch {

  }
  favs.forEach((id) => {
    const car = cars.find((c) => c.id === id);
    const chip = document.createElement("span");
    chip.className = "fav-chip";
    chip.innerHTML = `<span>${car ? car.brand + " " + car.model : "#" + id}</span><span class="x">✕</span>`;
    chip.querySelector(".x").onclick = () => toggleFav(id);
    wrap.appendChild(chip);
  });
}

function bind() {
  $("login-btn").onclick = login;
  $("logout-btn").onclick = logout;
  $("filter-btn").onclick = loadCars;
  $("filter-reset").onclick = () => {
    $("filter-brand").value = "";
    $("filter-price").value = "";
    loadCars();
  };
  $("car-add-btn").onclick = addCar;
  $("users-load").onclick = loadUsers;
  $("user-add-btn").onclick = addUser;
  $("login-password").addEventListener("keydown", (e) => e.key === "Enter" && login());
}

document.addEventListener("DOMContentLoaded", () => {
  bind();
  applyRole();
  loadCars();
  renderFavs();
});
