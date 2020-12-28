from rest_framework import serializers
from .models import SubscriptionUser
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
import random
import string
from django.contrib.auth.models import update_last_login
import stripe


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=SubscriptionUser.objects.all())],
    )
    first_name = serializers.CharField(required=True, max_length=32)
    last_name = serializers.CharField(required=True, max_length=32)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = SubscriptionUser
        fields = (
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        stripe_id = stripe.Customer.create(email=validated_data["email"])
        user = SubscriptionUser.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            stripe_id=stripe_id.id,
        )

        last_login = update_last_login(None, user)
        user.set_password(validated_data["password"])
        user.save()

        return user
