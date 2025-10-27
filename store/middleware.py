from django.http import HttpResponseBadRequest
from .models import Vendor

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.headers.get("X-Tenant-Domain") or request.get_host().split(":")[0]
        try:
            request.tenant = Vendor.objects.get(domain=domain)
        except Vendor.DoesNotExist:
            request.tenant = None
        return self.get_response(request)
