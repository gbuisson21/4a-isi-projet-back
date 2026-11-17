# Pol-eat-heck — API Documentation

REST API exposed by the FastAPI back-end (`4a-isi-projet-back`) and consumed by the front-end (`4a-isi-projet-front`).

> FastAPI also generates an interactive Swagger UI at `/docs` once the routes are implemented. This document is the **contract** agreed between front and back before (and during) implementation.

---

## Table of contents

- [General conventions](#general-conventions)
  - [Base URL](#base-url)
  - [Headers](#headers)
  - [Authentication](#authentication)
  - [Data types](#data-types)
  - [Errors](#errors)
- [Data models](#data-models)
- [Routes overview](#routes-overview)
- [1. Public routes](#1-public-routes)
- [2. User routes](#2-user-routes)
- [3. Admin routes](#3-admin-routes)
- [Notes](#notes)

---

## General conventions

### Base URL

All routes are prefixed with `/api` so they don't conflict with the static front-end files served by FastAPI.

```
http://<host>:8000/api
```

### Headers

| Header | Value | When | Description |
|---|---|---|---|
| `Content-Type` | `application/json` | Every request **with a body** (`POST`, `PUT`) | Format of the request body. |
| `Accept` | `application/json` | Optional | Expected response format. Every response is JSON. |
| `Authorization` | `Bearer <access_token>` | Every **🔒 User** and **🛡️ Admin** route | Token returned by [`POST /api/user/login`](#post-apiuserlogin). |

Every response is sent with `Content-Type: application/json` (except `204 No Content`, which has no body).

### Authentication

| Level | Meaning |
|---|---|
| 🌐 **Public** | No token needed. |
| 🔒 **User** | Valid token required (role `user` **or** `admin`). The account must not be locked. |
| 🛡️ **Admin** | Valid token required **and** role must be `admin`. |

- The token is a **JWT** returned by the login route. It is stateless, so it works with several back-end instances behind the load balancer.
- A locked account cannot log in (`403`), and its existing tokens are rejected (`403`).
- Admin accounts **cannot** be created through the API: they are created only with a command-line script (username + password), as required by the subject.

### Data types

| Type | JSON | Example | Notes |
|---|---|---|---|
| `integer` | number | `12` | |
| `number` | number | `8.50` | Prices, in euros, 2 decimals. |
| `string` | string | `"Croque-monsieur"` | |
| `boolean` | boolean | `true` | |
| `date` | string | `"2026-11-20"` | ISO 8601, `YYYY-MM-DD`. |
| `datetime` | string | `"2026-11-17T14:02:11"` | ISO 8601. |
| `enum` | string | `"pending"` | One of the listed values. |
| `T[]` | array | `[1, 2, 3]` | Array of `T`. |
| `T \| null` | | `null` | Nullable field. |

### Errors

Errors use the default FastAPI format:

```json
{ "detail": "Product not found" }
```

Validation errors (`422`, wrong type or missing field) are generated automatically by FastAPI:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "name"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

| Code | Meaning | Typical case |
|---|---|---|
| `400` Bad Request | A business rule is not respected | Pickup date is a closing day, not enough stock… |
| `401` Unauthorized | Missing, invalid or expired token / wrong credentials | No `Authorization` header |
| `403` Forbidden | Authenticated but not allowed | User calling an admin route, locked account |
| `404` Not Found | The resource doesn't exist | Unknown `product_id` |
| `409` Conflict | Conflict with existing data | Username already taken |
| `422` Unprocessable Entity | Body / params don't match the expected types | `"price": "abc"` |

---

## Data models

### `Product`

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | Unique identifier. |
| `name` | `string` | Product name. |
| `price` | `number` | Unit price in euros. |
| `stock` | `integer` | Available quantity. `0` = unavailable. |

```json
{ "id": 5, "name": "Cookie", "price": 1.50, "stock": 30 }
```

### `Menu`

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | Unique identifier. |
| `name` | `string` | Menu name. |
| `price` | `number` | Menu price in euros. |
| `start_date` | `date` | First day the menu is available. |
| `end_date` | `date` | Last day the menu is available (= `start_date` for a one-day menu). |
| `products` | `Product[]` | Products that make up the menu. |

```json
{
  "id": 2,
  "name": "Menu du jour",
  "price": 8.50,
  "start_date": "2026-11-16",
  "end_date": "2026-11-22",
  "products": [
    { "id": 1, "name": "Croque-monsieur", "price": 4.00, "stock": 20 },
    { "id": 5, "name": "Cookie", "price": 1.50, "stock": 30 }
  ]
}
```

### `User`

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | Unique identifier. |
| `username` | `string` | Unique username. |
| `role` | `enum` | `user` \| `admin` |
| `is_locked` | `boolean` | `true` if the account was locked by an admin. |
| `created_at` | `datetime` | Account creation date. |

> The password (hashed) is **never** returned.

### `Closure`

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | Unique identifier. |
| `date` | `date` | Closing day. |
| `reason` | `string \| null` | Optional reason (e.g. `"Bank holiday"`). |

### `Reservation`

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | Unique identifier. |
| `user` | `{ id: integer, username: string }` | Owner of the reservation. |
| `pickup_date` | `date` | Day the order will be picked up (and paid). |
| `status` | `enum` | `pending` (not picked up yet) \| `completed` (picked up and paid) \| `no_show` (never picked up) |
| `created_at` | `datetime` | Creation date. |
| `products` | `ReservationLine[]` | Products ordered. |
| `menus` | `ReservationLine[]` | Menus ordered. |
| `total_price` | `number` | Total to pay on pickup (payment is **not** handled by the app). |

`ReservationLine`:

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | Product or menu id. |
| `name` | `string` | Product or menu name. |
| `unit_price` | `number` | Price at the time of the reservation. |
| `quantity` | `integer` | Quantity ordered (≥ 1). |

```json
{
  "id": 14,
  "user": { "id": 3, "username": "jdoe" },
  "pickup_date": "2026-11-20",
  "status": "pending",
  "created_at": "2026-11-17T14:02:11",
  "products": [
    { "id": 5, "name": "Cookie", "unit_price": 1.50, "quantity": 2 }
  ],
  "menus": [
    { "id": 2, "name": "Menu du jour", "unit_price": 8.50, "quantity": 1 }
  ],
  "total_price": 11.50
}
```

### `PlanningDay`

| Field | Type | Description |
|---|---|---|
| `date` | `date` | The day. |
| `is_closed` | `boolean` | `true` if it's a closing day. |
| `closure_reason` | `string \| null` | Reason of the closure, if any. |
| `menus` | `Menu[]` | Menus available that day (empty if closed). |

---

## Routes overview

| # | Method | Route | Auth | Description |
|---|---|---|---|---|
| 1 | `GET` | [`/api/menus`](#get-apimenus) | 🌐 | List menus |
| 1 | `GET` | [`/api/menus/{menu_id}`](#get-apimenusmenu_id) | 🌐 | Get one menu |
| 1 | `GET` | [`/api/products`](#get-apiproducts) | 🌐 | List products |
| 1 | `GET` | [`/api/products/{product_id}`](#get-apiproductsproduct_id) | 🌐 | Get one product |
| 1 | `GET` | [`/api/planning`](#get-apiplanning) | 🌐 | Weekly planning (menus + closing days) |
| 2 | `POST` | [`/api/user/register`](#post-apiuserregister) | 🌐 | Create an account |
| 2 | `POST` | [`/api/user/login`](#post-apiuserlogin) | 🌐 | Log in |
| 2 | `PUT` | [`/api/user/change-password`](#put-apiuserchange-password) | 🔒 | Change password |
| 2 | `GET` | [`/api/user/profile`](#get-apiuserprofile) | 🔒 | Current user profile |
| 2 | `GET` | [`/api/user/reservations`](#get-apiuserreservations) | 🔒 | List my reservations |
| 2 | `POST` | [`/api/user/reservations`](#post-apiuserreservations) | 🔒 | Create a reservation |
| 2 | `DELETE` | [`/api/user/reservations/{reservation_id}`](#delete-apiuserreservationsreservation_id) | 🔒 | Cancel my reservation |
| 3 | `POST` | [`/api/admin/products`](#post-apiadminproducts) | 🛡️ | Create a product |
| 3 | `PUT` | [`/api/admin/products/{product_id}`](#put-apiadminproductsproduct_id) | 🛡️ | Update a product |
| 3 | `DELETE` | [`/api/admin/products/{product_id}`](#delete-apiadminproductsproduct_id) | 🛡️ | Delete a product |
| 3 | `PUT` | [`/api/admin/products/{product_id}/stock`](#put-apiadminproductsproduct_idstock) | 🛡️ | Set stock / availability |
| 3 | `POST` | [`/api/admin/menus`](#post-apiadminmenus) | 🛡️ | Create a menu |
| 3 | `PUT` | [`/api/admin/menus/{menu_id}`](#put-apiadminmenusmenu_id) | 🛡️ | Update a menu |
| 3 | `DELETE` | [`/api/admin/menus/{menu_id}`](#delete-apiadminmenusmenu_id) | 🛡️ | Delete a menu |
| 3 | `POST` | [`/api/admin/closures`](#post-apiadminclosures) | 🛡️ | Add a closing day |
| 3 | `DELETE` | [`/api/admin/closures/{closure_id}`](#delete-apiadminclosuresclosure_id) | 🛡️ | Remove a closing day |
| 3 | `PUT` | [`/api/admin/users/{user_id}/lock`](#put-apiadminusersuser_idlock) | 🛡️ | Lock / unlock a user |
| 3 | `GET` | [`/api/admin/reservations`](#get-apiadminreservations) | 🛡️ | List all reservations |
| 3 | `POST` | [`/api/admin/reservations/{reservation_id}/check`](#post-apiadminreservationsreservation_idcheck) | 🛡️ | Check a reservation at pickup |
| 3 | `DELETE` | [`/api/admin/reservations/{reservation_id}`](#delete-apiadminreservationsreservation_id) | 🛡️ | Delete a reservation |

---

## 1. Public routes

### `GET /api/menus`

List the menus. Anyone can see them, without being logged in.

**Auth:** 🌐 Public

**Headers:** none required.

**Query parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `date` | `date` | No | Only return the menus available on this day (`start_date <= date <= end_date`). |

**Response** `200 OK` — `Menu[]`

```json
[
  {
    "id": 2,
    "name": "Menu du jour",
    "price": 8.50,
    "start_date": "2026-11-16",
    "end_date": "2026-11-22",
    "products": [ { "id": 1, "name": "Croque-monsieur", "price": 4.00, "stock": 20 } ]
  }
]
```

**Errors:** `422` if `date` isn't a valid date.

---

### `GET /api/menus/{menu_id}`

Get the details of one menu.

**Auth:** 🌐 Public

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `menu_id` | `integer` | Menu id. |

**Response** `200 OK` — `Menu`

**Errors:** `404` menu not found.

---

### `GET /api/products`

List all the products with their stock.

**Auth:** 🌐 Public

**Response** `200 OK` — `Product[]`

```json
[
  { "id": 1, "name": "Croque-monsieur", "price": 4.00, "stock": 20 },
  { "id": 5, "name": "Cookie", "price": 1.50, "stock": 0 }
]
```

---

### `GET /api/products/{product_id}`

Get one product.

**Auth:** 🌐 Public

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `product_id` | `integer` | Product id. |

**Response** `200 OK` — `Product`

**Errors:** `404` product not found.

---

### `GET /api/planning`

Get the planning, day by day: whether the place is open and which menus are available. Used by the front to display the week and by users to choose a pickup date.

**Auth:** 🌐 Public

**Query parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `start_date` | `date` | No | Monday of the current week | First day of the planning. |
| `end_date` | `date` | No | `start_date` + 6 days | Last day of the planning. |

**Response** `200 OK` — `PlanningDay[]`

```json
[
  {
    "date": "2026-11-16",
    "is_closed": false,
    "closure_reason": null,
    "menus": [ { "id": 2, "name": "Menu du jour", "price": 8.50, "start_date": "2026-11-16", "end_date": "2026-11-22", "products": [] } ]
  },
  {
    "date": "2026-11-17",
    "is_closed": true,
    "closure_reason": "Staff training",
    "menus": []
  }
]
```

**Errors:** `400` if `end_date` is before `start_date` · `422` invalid date format.

---

## 2. User routes

### `POST /api/user/register`

Create a standard user account. The password is **generated randomly by the server** and returned **only in this response** — it can't be retrieved later (no emailing).

**Auth:** 🌐 Public

**Headers**

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `username` | `string` | Yes | Unique username (3–30 characters). |

```json
{ "username": "jdoe" }
```

**Response** `201 Created`

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | New user id. |
| `username` | `string` | Username. |
| `password` | `string` | Generated password, shown **once**. |

```json
{ "id": 3, "username": "jdoe", "password": "k7Fq-2xPm-9Lzr" }
```

**Errors:** `409` username already taken · `422` missing / invalid username.

---

### `POST /api/user/login`

Log in with username and password. Returns the token to put in the `Authorization` header of the next requests.

**Auth:** 🌐 Public

**Headers**

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `username` | `string` | Yes | Username. |
| `password` | `string` | Yes | Password. |

```json
{ "username": "jdoe", "password": "k7Fq-2xPm-9Lzr" }
```

**Response** `200 OK`

| Field | Type | Description |
|---|---|---|
| `access_token` | `string` | JWT to send as `Authorization: Bearer <access_token>`. |
| `token_type` | `string` | Always `"bearer"`. |
| `role` | `enum` | `user` \| `admin` — lets the front show the admin pages. |

```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer", "role": "user" }
```

**Errors:** `401` wrong username or password · `403` account locked · `422` missing field.

---

### `PUT /api/user/change-password`

Change the password of the logged-in user.

**Auth:** 🔒 User

**Headers**

| Header | Value |
|---|---|
| `Authorization` | `Bearer <access_token>` |
| `Content-Type` | `application/json` |

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `old_password` | `string` | Yes | Current password. |
| `new_password` | `string` | Yes | New password (min. 8 characters, different from the old one). |

```json
{ "old_password": "k7Fq-2xPm-9Lzr", "new_password": "MyN3wP@ssword" }
```

**Response** `204 No Content`

**Errors:** `400` new password too short or same as the old one · `401` not logged in / `old_password` is wrong · `403` account locked · `422` missing field.

---

### `GET /api/user/profile`

Get the profile of the logged-in user.

**Auth:** 🔒 User

**Headers**

| Header | Value |
|---|---|
| `Authorization` | `Bearer <access_token>` |

**Response** `200 OK` — `User`

```json
{ "id": 3, "username": "jdoe", "role": "user", "is_locked": false, "created_at": "2026-11-17T13:58:40" }
```

**Errors:** `401` not logged in · `403` account locked.

---

### `GET /api/user/reservations`

List the reservations of the logged-in user.

**Auth:** 🔒 User

**Headers**

| Header | Value |
|---|---|
| `Authorization` | `Bearer <access_token>` |

**Query parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `status` | `enum` | No | Filter: `pending` \| `completed` \| `no_show`. |

**Response** `200 OK` — `Reservation[]` (sorted by `pickup_date`, most recent first)

**Errors:** `401` not logged in · `403` account locked.

---

### `POST /api/user/reservations`

Order products and/or menus in advance for a given pickup day. Payment is made on pickup. The stock of the ordered products (and of the products contained in the ordered menus) is decreased.

**Auth:** 🔒 User

**Headers**

| Header | Value |
|---|---|
| `Authorization` | `Bearer <access_token>` |
| `Content-Type` | `application/json` |

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `pickup_date` | `date` | Yes | Pickup day. Must be today or later, and not a closing day. |
| `products` | `{ product_id: integer, quantity: integer }[]` | No* | Products to order. |
| `menus` | `{ menu_id: integer, quantity: integer }[]` | No* | Menus to order. Each menu must be available on `pickup_date`. |

\* At least one of `products` / `menus` must be non-empty. `quantity` ≥ 1.

```json
{
  "pickup_date": "2026-11-20",
  "products": [ { "product_id": 5, "quantity": 2 } ],
  "menus": [ { "menu_id": 2, "quantity": 1 } ]
}
```

**Response** `201 Created` — `Reservation`

**Errors:**
- `400` `pickup_date` is in the past or a closing day · menu not available on that date · not enough stock · empty order
- `401` not logged in
- `403` account locked
- `404` a `product_id` or `menu_id` doesn't exist
- `422` invalid body

---

### `DELETE /api/user/reservations/{reservation_id}`

Cancel one of my reservations. Only possible if it's still `pending` and the pickup date is not passed. The stock is restored.

**Auth:** 🔒 User

**Headers**

| Header | Value |
|---|---|
| `Authorization` | `Bearer <access_token>` |

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `reservation_id` | `integer` | Reservation id. |

**Response** `204 No Content`

**Errors:** `400` reservation not `pending` or pickup date passed · `401` not logged in · `403` locked account, or the reservation belongs to another user · `404` reservation not found.

---

## 3. Admin routes

All routes below require:

| Header | Value |
|---|---|
| `Authorization` | `Bearer <access_token>` (of an **admin** account) |
| `Content-Type` | `application/json` (only for routes with a body) |

Common errors for every admin route: `401` not logged in · `403` not an admin.

### `POST /api/admin/products`

Create a product.

**Auth:** 🛡️ Admin

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | Yes | Product name. |
| `price` | `number` | Yes | Unit price (≥ 0). |
| `stock` | `integer` | No (default `0`) | Initial stock (≥ 0). |

```json
{ "name": "Cookie", "price": 1.50, "stock": 30 }
```

**Response** `201 Created` — `Product`

**Errors:** `422` invalid body.

---

### `PUT /api/admin/products/{product_id}`

Update a product. Only the fields sent are modified.

**Auth:** 🛡️ Admin

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `product_id` | `integer` | Product id. |

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | No | New name. |
| `price` | `number` | No | New price (≥ 0). |

```json
{ "price": 1.80 }
```

**Response** `200 OK` — `Product` (updated)

**Errors:** `404` product not found · `422` invalid body.

---

### `DELETE /api/admin/products/{product_id}`

Delete a product.

**Auth:** 🛡️ Admin

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `product_id` | `integer` | Product id. |

**Response** `204 No Content`

**Errors:** `404` product not found · `409` product is used in a menu or in a `pending` reservation.

---

### `PUT /api/admin/products/{product_id}/stock`

Set the stock (availability) of a product. A stock of `0` makes the product unavailable.

**Auth:** 🛡️ Admin

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `product_id` | `integer` | Product id. |

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `stock` | `integer` | Yes | New stock (≥ 0). |

```json
{ "stock": 0 }
```

**Response** `200 OK` — `Product` (updated)

**Errors:** `404` product not found · `422` negative or missing stock.

---

### `POST /api/admin/menus`

Create a menu made of existing products, with its availability period (one day, one week…).

**Auth:** 🛡️ Admin

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | Yes | Menu name. |
| `price` | `number` | Yes | Menu price (≥ 0). |
| `start_date` | `date` | Yes | First day of availability. |
| `end_date` | `date` | Yes | Last day of availability (≥ `start_date`). |
| `product_ids` | `integer[]` | Yes | Ids of the products in the menu (at least 1). |

```json
{
  "name": "Menu du jour",
  "price": 8.50,
  "start_date": "2026-11-16",
  "end_date": "2026-11-22",
  "product_ids": [1, 5]
}
```

**Response** `201 Created` — `Menu`

**Errors:** `400` `end_date` before `start_date` or empty `product_ids` · `404` a product doesn't exist · `422` invalid body.

---

### `PUT /api/admin/menus/{menu_id}`

Update a menu (name, price, products, availability dates). Only the fields sent are modified.

**Auth:** 🛡️ Admin

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `menu_id` | `integer` | Menu id. |

**Body** — same fields as [`POST /api/admin/menus`](#post-apiadminmenus), all optional.

```json
{ "end_date": "2026-11-18" }
```

**Response** `200 OK` — `Menu` (updated)

**Errors:** `400` `end_date` before `start_date` · `404` menu or product not found · `422` invalid body.

---

### `DELETE /api/admin/menus/{menu_id}`

Delete a menu.

**Auth:** 🛡️ Admin

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `menu_id` | `integer` | Menu id. |

**Response** `204 No Content`

**Errors:** `404` menu not found · `409` menu is in a `pending` reservation.

---

### `POST /api/admin/closures`

Declare a specific closing day. No reservation can be made for that day.

**Auth:** 🛡️ Admin

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `date` | `date` | Yes | Closing day. |
| `reason` | `string` | No | Reason shown in the planning. |

```json
{ "date": "2026-12-25", "reason": "Christmas" }
```

**Response** `201 Created` — `Closure`

```json
{ "id": 4, "date": "2026-12-25", "reason": "Christmas" }
```

**Errors:** `409` this day is already closed · `422` invalid date.

---

### `DELETE /api/admin/closures/{closure_id}`

Remove a closing day (the place is open again that day).

**Auth:** 🛡️ Admin

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `closure_id` | `integer` | Closure id. |

**Response** `204 No Content`

**Errors:** `404` closure not found.

---

### `PUT /api/admin/users/{user_id}/lock`

Lock or unlock a user account (e.g. after repeated `no_show` reservations). A locked user can't log in or use 🔒 routes.

**Auth:** 🛡️ Admin

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `user_id` | `integer` | User id (visible in the `user` field of reservations). |

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `locked` | `boolean` | Yes | `true` to lock, `false` to unlock. |

```json
{ "locked": true }
```

**Response** `200 OK` — `User` (updated)

**Errors:** `400` an admin can't lock an admin account · `404` user not found · `422` invalid body.

---

### `GET /api/admin/reservations`

List all the reservations (e.g. to prepare the orders of the day).

**Auth:** 🛡️ Admin

**Query parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `pickup_date` | `date` | No | Only the reservations for this day. |
| `status` | `enum` | No | `pending` \| `completed` \| `no_show` |
| `user_id` | `integer` | No | Only the reservations of this user. |

**Response** `200 OK` — `Reservation[]`

**Errors:** `422` invalid query parameter.

---

### `POST /api/admin/reservations/{reservation_id}/check`

Check a reservation when the customer comes (or doesn't come) to pick it up. Payment is made at this moment, outside the app.

**Auth:** 🛡️ Admin

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `reservation_id` | `integer` | Reservation id. |

**Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | `enum` | Yes | `completed` (picked up and paid) \| `no_show` (customer didn't come). |

```json
{ "status": "completed" }
```

**Response** `200 OK` — `Reservation` (updated)

**Errors:** `400` reservation is not `pending` anymore · `404` reservation not found · `422` invalid status.

---

### `DELETE /api/admin/reservations/{reservation_id}`

Delete any reservation. If it was `pending`, the stock is restored.

**Auth:** 🛡️ Admin

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `reservation_id` | `integer` | Reservation id. |

**Response** `204 No Content`

**Errors:** `404` reservation not found.

---

## Notes

- **Admin creation:** only through a CLI script on the server (username + password), never through the API.
- **CORS:** if the front is served by FastAPI itself (same origin), nothing to configure. If it's served elsewhere during development (e.g. Live Server on another port), add FastAPI's `CORSMiddleware`.
- **Passwords** are stored hashed (e.g. `bcrypt` / `argon2`), never in clear text.
