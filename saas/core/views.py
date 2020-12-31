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

    def get_post_response_data(self, request, token, instance):
        UserSerializer = self.get_user_serializer_class()

        data = {"expiry": self.format_expiry_datetime(instance.expiry), "token": token}
        if UserSerializer is not None:
            user = UserSerializer(request.user, context=self.get_context()).data
            data["user"] = user
        return data


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


class ProductsView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)

    def list(self, request):
        products = stripe.Product.list()
        index = 0
        for product in products.data:
            prices = stripe.Price.list(product=product["id"])
            products.data[index]["prices"] = prices.data
            index += 1
        return Response(products.data)


class CheckoutView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        print(request.data)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": request.data["price_id"],
                    "quantity": 1,
                }
            ],
            success_url="http://localhost:3000" + "/success.html",
            cancel_url="http://localhost:3000" + "/cancel.html",
        )
        print(type(checkout_session.id))
        return Response({"id": checkout_session.id})
