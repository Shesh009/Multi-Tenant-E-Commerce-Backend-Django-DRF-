from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet
from .views_auth import CustomerRegisterView, StaffRegisterView, TenantTokenObtainPairView, VendorRegisterView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("auth/login/", TenantTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("", include(router.urls)),
    path("auth/register-vendor/", VendorRegisterView.as_view()),
    path("auth/register-customer/", CustomerRegisterView.as_view(), name="customer_register"),
    path("auth/register-staff/", StaffRegisterView.as_view(), name="staff_register"),
]
