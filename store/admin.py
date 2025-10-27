from django.contrib import admin
from .models import Vendor, User, Product, Order, OrderItem

admin.site.register([Vendor, User, Product, Order, OrderItem])