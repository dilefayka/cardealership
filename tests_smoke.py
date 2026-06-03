
from fastapi.testclient import TestClient

from app.main import app

ok = 0
fail = 0


def check(label, condition):
    global ok, fail
    if condition:
        ok += 1
        print(f"[PASS] {label}")
    else:
        fail += 1
        print(f"[FAIL] {label}")


def run(client):
    # Публичное чтение
    r = client.get("/users")
    check("GET /users -> 200", r.status_code == 200)
    check("GET /users seeded >= 2", len(r.json()) >= 2)

    r = client.get("/users/1")
    check("GET /users/1 -> 200", r.status_code == 200)

    r = client.get("/users/999")
    check("GET /users/999 -> 404", r.status_code == 404)
    check("404 code=not_found", r.json()["error"]["code"] == "not_found")

    # Доступ без токена
    r = client.post("/users", json={"name": "X", "email": "x@example.com"})
    check("POST /users без токена -> 401", r.status_code == 401)

    # guest -> запись запрещена
    r = client.post("/auth/login", json={"username": "guest", "password": "guest123"})
    check("login guest -> 200", r.status_code == 200)
    guest = {"Authorization": f"Bearer {r.json()['token']}"}
    r = client.post("/users", json={"name": "Y", "email": "y@example.com"}, headers=guest)
    check("guest POST /users -> 403", r.status_code == 403)

    # Неверный пароль
    r = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    check("login неверный пароль -> 401", r.status_code == 401)

    # admin
    r = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    H = {"Authorization": f"Bearer {r.json()['token']}"}

    r = client.post("/users", json={"name": "Олег", "email": "oleg@example.com", "age": 40}, headers=H)
    check("admin POST /users -> 201", r.status_code == 201)
    check("новый пользователь имеет id", isinstance(r.json().get("id"), int))

    r = client.post("/users", json={"name": "Олег2", "email": "oleg@example.com"}, headers=H)
    check("дубликат email -> 409", r.status_code == 409)

    r = client.post("/users", json={"name": "Z", "email": "not-an-email"}, headers=H)
    check("невалидный email -> 422", r.status_code == 422)

    r = client.post("/users", json={"name": "   ", "email": "blank@example.com"}, headers=H)
    check("пустое имя -> 422", r.status_code == 422)

    # Автомобили
    r = client.get("/cars")
    check("GET /cars -> 200", r.status_code == 200 and len(r.json()) >= 3)

    r = client.get("/cars?brand=Toyota")
    check("фильтр по марке", all(c["brand"] == "Toyota" for c in r.json()))

    r = client.get("/cars?max_price=3000000")
    check("фильтр по цене", all(c["price"] <= 3000000 for c in r.json()))

    r = client.post("/cars", json={"brand": "Audi", "model": "A4", "year": 2023, "price": 3900000, "body_type": "sedan"}, headers=H)
    check("admin POST /cars -> 201", r.status_code == 201)
    car_id = r.json()["id"]

    r = client.post("/cars", json={"brand": "X", "model": "Y", "year": 1800, "price": 100}, headers=H)
    check("год вне диапазона -> 422", r.status_code == 422)

    r = client.delete(f"/cars/{car_id}", headers=H)
    check("admin DELETE /cars -> 204", r.status_code == 204)
    r = client.get(f"/cars/{car_id}")
    check("удалённый авто -> 404", r.status_code == 404)

    r = client.delete("/cars/1", headers=guest)
    check("guest DELETE /cars -> 403", r.status_code == 403)


if __name__ == "__main__":
    with TestClient(app) as client:
        run(client)
    print(f"\nИТОГО: PASS={ok} FAIL={fail}")
    raise SystemExit(1 if fail else 0)
