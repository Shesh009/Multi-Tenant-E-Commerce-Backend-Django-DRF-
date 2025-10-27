from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from .permissions import IsTenantMatch, IsStaffOrOwnerForWrite
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsTenantMatch, IsStaffOrOwnerForWrite]

    def get_queryset(self):
        return Product.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        tenant = self.request.tenant
        if user.role not in ["owner", "staff"]:
            raise PermissionDenied("Only owner or staff can add products.")
        serializer.save(
            vendor=tenant,
            assigned_to=user if user.role == "staff" else None
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        if user.role == "staff" and instance.assigned_to_id != user.id:
            raise PermissionDenied("You can only update your assigned products.")
        serializer.save()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsTenantMatch, IsStaffOrOwnerForWrite]

    def get_queryset(self):
        return Order.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        tenant = self.request.tenant
        if user.role == "customer":
            serializer.save(vendor=tenant, customer=user)
        elif user.role == "staff":
            serializer.save(vendor=tenant, assigned_to=user)
        elif user.role == "owner":
            serializer.save(vendor=tenant)
        else:
            raise PermissionDenied("Not authorized to create orders.")

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        if user.role == "staff" and instance.assigned_to_id != user.id:
            raise PermissionDenied("You can only update your assigned orders.")
        if user.role == "customer":
            raise PermissionDenied("Customers cannot update orders.")
        serializer.save()
