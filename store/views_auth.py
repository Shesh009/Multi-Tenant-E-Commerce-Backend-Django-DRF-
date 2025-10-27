# store/views_auth.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .tokens import TenantTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from .models import User, Vendor, CustomerProfile
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Vendor, User
from django.contrib.auth.hashers import make_password

class TenantTokenObtainPairView(TokenObtainPairView):
    serializer_class = TenantTokenObtainPairSerializer

class VendorRegisterView(APIView):
    permission_classes = []

    def post(self, request):
        data = request.data
        v = Vendor.objects.create(
            name=data["vendor"]["name"],
            domain=data["vendor"]["domain"],
            contact_email=data["vendor"]["contact_email"]
        )
        user_data = data["user"]
        u = User.objects.create(
            username=user_data["username"],
            email=user_data.get("email",""),
            password=make_password(user_data["password"]),
            role=User.OWNER,
            vendor=v
        )
        return Response({"vendor_id": v.id, "owner_id": u.id}, status=status.HTTP_201_CREATED)


class CustomerRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        request = self.context["request"]
        tenant = getattr(request, "tenant", None)
        if not tenant:
            raise serializers.ValidationError("Tenant not found. Please include X-Tenant-Domain header.")

        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            role=User.CUSTOMER,
            vendor=tenant,
        )
        CustomerProfile.objects.create(
            user=user,
            vendor=tenant,
            phone=validated_data.get("phone", ""),
            address=validated_data.get("address", "")
        )
        return user


class CustomerRegisterView(APIView):
    permission_classes = []

    def post(self, request):
        domain = request.headers.get("X-Tenant-Domain")
        if not domain:
            return Response({"detail": "Missing X-Tenant-Domain"}, status=400)
        vendor = Vendor.objects.get(domain=domain)
        data = request.data
        u = User.objects.create(
            username=data["username"],
            email=data.get("email", ""),
            password=make_password(data["password"]),
            role=User.CUSTOMER,
            vendor=vendor
        )
        return Response({"id": u.id, "username": u.username, "vendor": vendor.name, "role": u.role}, status=201)

class StaffRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        tenant = request.tenant

        if not user.is_owner() or user.vendor_id != tenant.id:
            raise serializers.ValidationError("Only store owners can create staff accounts.")

        staff_user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            role=User.STAFF,
            vendor=tenant
        )
        return staff_user


class StaffRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != User.OWNER:
            return Response({"detail": "Only owners can add staff"}, status=403)
        vendor = request.user.vendor
        data = request.data
        u = User.objects.create(
            username=data["username"],
            email=data.get("email", ""),
            password=make_password(data["password"]),
            role=User.STAFF,
            vendor=vendor
        )
        return Response({"id": u.id, "username": u.username, "role": u.role}, status=201)
