# Multi-Tenant E-Commerce Backend (Django + DRF)

A scalable multi-tenant e-commerce backend built with Django REST Framework (DRF).  
This system isolates vendor data using domain-based multi-tenancy and enforces role-based access control (RBAC) for Owners, Staff, and Customers.

Each vendor operates as an independent tenant with isolated products, orders, and customers — while sharing a common codebase and infrastructure.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Multi-Tenancy Implementation](#multi-tenancy-implementation)
- [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)

---

## Overview

The backend provides APIs for managing:

- Vendors (tenants)
- Users (owners, staff, customers)
- Products
- Orders and order items
- Customer profiles

It supports:

- Multi-tenant isolation via middleware
- JWT authentication (with tenant information)
- Role-based permissions
- Clean serializer and queryset design for tenant safety

---

## Architecture

### Core Components

| Component | Purpose |
|------------|----------|
| Vendor | Represents each tenant (store) with a unique domain. |
| User | Extends Django’s user model with a role and optional vendor link. |
| Product | Vendor-specific items managed by owners or assigned staff. |
| Order | Vendor-specific orders created by customers, processed by staff or owners. |
| TenantMiddleware | Resolves tenant (vendor) from domain header for every request. |
| Permissions | Custom DRF permissions to enforce tenant and role-based access. |
| QuerySet Managers | Automatically filter data based on user roles and tenant context. |

---

## Setup & Installation

Follow these steps to install and run the project locally.

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/multi-tenant-ecommerce.git
cd multi-tenant-ecommerce
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Server starts at:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 7. Test API Health

Visit:
[http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

---

## Multi-Tenancy Implementation

Multi-tenancy ensures that each Vendor operates in isolation, sharing infrastructure but not data.

### Tenant Identification

Implemented in `store/middleware.py`:

```python
domain = request.headers.get("X-Tenant-Domain") or request.get_host().split(":")[0]
request.tenant = Vendor.objects.get(domain=domain)
```

* The middleware runs before the view.
* It resolves `request.tenant` based on:

  * The `X-Tenant-Domain` header, or
  * The subdomain part of the host.
* If no tenant is found, it sets `request.tenant = None` (used for open endpoints like registration).

### Tenant Validation

Each API request requires:

```
X-Tenant-Domain: mystore.example.com
```

### Tenant Permission Check

`IsTenantMatch` ensures that the JWT’s `tenant_id` matches the resolved tenant:

```python
token_tenant_id = token.payload.get("tenant_id")
return str(token_tenant_id) == str(request.tenant.id)
```

This prevents users from accessing data belonging to another tenant.

---

## Role-Based Access Control (RBAC)

Each user is assigned one of the following roles:

| Role     | Capabilities                                                   |
| -------- | -------------------------------------------------------------- |
| Owner    | Full CRUD access to all vendor data (products, orders, staff). |
| Staff    | Limited CRUD access to assigned products and orders only.      |
| Customer | Can browse products, create orders, and view own orders.       |

### Implementation Highlights

**Custom DRF Permissions**

* `IsTenantMatch`: Validates tenant context.
* `IsStaffOrOwnerForWrite`: Restricts modification privileges.

**Scoped QuerySets**

* `ProductQuerySet.for_user()`
* `OrderQuerySet.for_user()`

These automatically return records visible to that user based on role.

Example:
A staff user can only view or edit products where:

```python
product.vendor == user.vendor and product.assigned_to == user
```

---

## API Endpoints

All requests require the header:

```
X-Tenant-Domain: mystore.example.com
```

**Base URL:**
[http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

### Authentication

| Method | Endpoint             | Description                                      |
| ------ | -------------------- | ------------------------------------------------ |
| POST   | /auth/register/      | Register a new user (owner, staff, or customer). |
| POST   | /auth/login/         | Obtain JWT access and refresh tokens.            |

<!-- ### Vendors

| Method | Endpoint       | Description              | Access                       |
| ------ | -------------- | ------------------------ | ---------------------------- |
| GET    | /vendors/      | List all vendors.        | Admin only                   |
| POST   | /vendors/      | Create a new vendor.     | Admin or public registration |
| GET    | /vendors/{id}/ | Retrieve vendor details. | All roles                    | -->

### Products

| Method | Endpoint        | Description                          | Access                 |
| ------ | --------------- | ------------------------------------ | ---------------------- |
| GET    | /products/      | List all products of current tenant. | All                    |
| POST   | /products/      | Create a new product.                | Owner / Assigned Staff |
| PUT    | /products/{id}/ | Update a product.                    | Owner / Assigned Staff |
| DELETE | /products/{id}/ | Delete a product.                    | Owner only             |

**Product Fields:**

```json
{
  "name": "Laptop",
  "description": "14-inch business laptop",
  "price": "1299.99",
  "inventory": 50
}
```

### Orders

| Method | Endpoint      | Description                          | Access                                  |
| ------ | ------------- | ------------------------------------ | --------------------------------------- |
| GET    | /orders/      | List orders (scoped by role).        | Owner, Staff, Customer                  |
| POST   | /orders/      | Create a new order (with add_items). | Customer                                |
| GET    | /orders/{id}/ | View a specific order.               | Owner, Staff (assigned), Customer (own) |
| PATCH  | /orders/{id}/ | Update order status.                 | Owner, Staff (assigned)                 |

**Order Example (POST /orders/):**

```json
{
  "add_items": [
    { "product": 1, "quantity": 2 },
    { "product": 3, "quantity": 1 }
  ]
}
```

### Customers

| Method | Endpoint         | Description                           |
| ------ | ---------------- | ------------------------------------- |
| GET    | /customers/      | List customers of the current vendor. |
| POST   | /customers/      | Create a customer profile.            |
| GET    | /customers/{id}/ | Retrieve a customer’s profile.        |

---

## Usage Examples

### Headers

```
Authorization: Bearer <access_token>
X-Tenant-Domain: mystore.example.com
Content-Type: application/json
```

### Example Request

```bash
GET http://127.0.0.1:8000/api/products/
```

### Example Response

```json
[
  {
    "id": 1,
    "name": "Smartphone",
    "price": "699.00",
    "inventory": 20,
    "vendor": 3
  }
]
```

---

## Project Structure

```
.
├── Multi-Tenant Collection.postman_collection.json
├── db.sqlite3
├── ecommerce
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── readme.md
├── requirements.txt
└── store
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── managers.py
    ├── middleware.py
    ├── migrations
    │   ├── 0001_initial.py
    │   ├── __init__.py
    ├── models.py
    ├── permissions.py
    ├── serializers.py
    ├── tests.py
    ├── tokens.py
    ├── urls.py
    ├── views.py
    └── views_auth.py
```
