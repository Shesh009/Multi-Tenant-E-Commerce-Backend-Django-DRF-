from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        token["tenant_id"] = user.vendor_id if user.vendor_id else None
        return token
