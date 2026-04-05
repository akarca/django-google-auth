from django.conf import settings


def get_client_id():
    return getattr(settings, "GOOGLE_CLIENT_ID", "")


def get_login_redirect_url():
    return getattr(settings, "LOGIN_REDIRECT_URL", "/")


def get_login_url():
    return getattr(settings, "LOGIN_URL", "/accounts/login/")
