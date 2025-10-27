from django.db import models
from django.contrib.auth.models import AbstractUser

from store.managers import OrderQuerySet, ProductQuerySet

class Vendor(models.Model):
    name = models.CharField(max_length=150)
    contact_email = models.EmailField()
    domain = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    OWNER = "owner"
    STAFF = "staff"
    CUSTOMER = "customer"
    ROLE_CHOICES = [
        (OWNER, "Owner"),
        (STAFF, "Staff"),
        (CUSTOMER, "Customer"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.CASCADE)

    def is_owner(self):
        return self.role == self.OWNER

    def is_staff_role(self):
        return self.role == self.STAFF

    def is_customer(self):
        return self.role == self.CUSTOMER

class Product(models.Model):
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.PositiveIntegerField(default=0)
    assigned_to = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_products')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} ({self.vendor})"

class CustomerProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_profiles")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="customers")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

class Order(models.Model):
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name="orders")
    customer = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default="created")
    assigned_to = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_orders')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrderQuerySet.as_manager()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
