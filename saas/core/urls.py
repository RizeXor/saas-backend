from django.urls import path, include
from knox import views as knox_views
from .views import (
    LoginView,
    RegisterView,
    SubscriptionsView,
    MeView,
    ProductsView,
    CheckoutView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth_register"),
    path("auth/login/", LoginView.as_view(), name="knox_login"),
    path("auth/logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("auth/logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path("subscriptions/", SubscriptionsView.as_view(), name="list_subscriptions"),
    path("me/", MeView.as_view(), name="user_me"),
    path("products/", ProductsView.as_view(), name="products_list"),
    path("checkout/", CheckoutView.as_view(), name="checkout_view"),
]
