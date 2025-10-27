from django.db import models

class ProductQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_anonymous:
            return self.none()

        qs = self
        if user.role == "owner":
            return qs.filter(vendor=user.vendor)
        elif user.role == "staff":
            return qs.filter(vendor=user.vendor, assigned_to=user)
        elif user.role == "customer":
            return qs.filter(vendor=user.vendor)
        return self.none()


class OrderQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_anonymous:
            return self.none()

        qs = self
        if user.role == "owner":
            return qs.filter(vendor=user.vendor)
        elif user.role == "staff":
            return qs.filter(vendor=user.vendor, assigned_to=user)
        elif user.role == "customer":
            return qs.filter(vendor=user.vendor, customer=user)
        return self.none()
