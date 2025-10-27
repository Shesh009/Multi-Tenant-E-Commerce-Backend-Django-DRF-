from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from .models import Product, Order, OrderItem, Vendor

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "vendor", "name", "description", "price", "inventory"]
        read_only_fields = ["vendor"]

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_price"]
        read_only_fields = ["unit_price", "product_name"]

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField(read_only=True)
    add_items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Order
        fields = [
            "id", "vendor", "customer", "status",
            "total", "created_at", "items", "add_items"
        ]
        read_only_fields = ["vendor", "customer", "total", "created_at"]

    def get_items(self, obj):
        return [
            {
                "id": item.id,
                "product": item.product_id,
                "product_name": item.product.name if item.product else None,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
            }
            for item in obj.items.all()
        ]

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("add_items", [])
        if not items_data:
            raise serializers.ValidationError("Order must contain at least one item.")

        order = Order.objects.create(**validated_data)
        total = 0

        for item_data in items_data:
            product = Product.objects.get(pk=item_data["product"])
            quantity = int(item_data["quantity"])

            if product.inventory < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.inventory}"
                )

            product.inventory -= quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )

            total += product.price * quantity

        order.total = total
        order.save()
        return order

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
