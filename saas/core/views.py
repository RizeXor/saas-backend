from django.contrib.auth import login

from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from .models import SubscriptionUser
from .serializers import RegisterSerializer
from rest_framework import generics
from rest_framework.response import Response
import stripe


class RegisterView(generics.CreateAPIView):
    queryset = SubscriptionUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class SubscriptionsView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        products = stripe.Subscription.list(
            limit=3,
            customer=request.user.stripe_id,
            expand=["data.plan.product"],
        )
        print(products)
        subscriptions = []
        for i in products["data"]:
            plan = i["plan"]
            product = plan["product"]
            subscriptions.append(
                {
                    "current_period_end": i["current_period_end"],
                    "current_period_start": i["current_period_start"],
                    "days_until_due": i["days_until_due"],
                    "status": i["status"],
                    "plan": {
                        "amount": plan["amount"],
                        "interval": plan["interval"],
                        "currency": plan["currency"],
                        "product": product,
                    },
                }
            )
        return Response(subscriptions)


class MeView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        user = request.user
        return Response(
            {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )
