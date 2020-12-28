from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth import get_user_model
from django.utils import timezone
import stripe


class SubscriptionUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, stripe_id, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            stripe_id=stripe_id,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    # TODO: fetch actual stripe customer ID
    def create_superuser(self, email, first_name, last_name, stripe_id, password=None):
        stripe_id = stripe.Customer.create(email=email)
        print(stripe_id.id)
        user = self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            stripe_id=stripe_id.id,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class SubscriptionUser(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    stripe_id = models.CharField(max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = SubscriptionUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "stripe_id"]

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin
