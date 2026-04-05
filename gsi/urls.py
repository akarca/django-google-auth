from django.urls import path

from . import views

app_name = "gsi"

urlpatterns = [
    path("accounts/google/callback/", views.google_callback, name="callback"),
]
