import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .conf import get_client_id, get_login_redirect_url, get_login_url

logger = logging.getLogger(__name__)
User = get_user_model()


@csrf_exempt
def google_callback(request):
    """
    Handle Google Sign-In callback.

    Receives a Google JWT credential via POST, verifies it, then:
    - If email matches an existing user → log them in
    - If no matching user → create a new account with unusable password

    Calls GSI_CALLBACK(request, user, created) hook if defined in settings
    for project-specific logic (cart migration, etc.)
    """
    if request.method != "POST":
        return redirect(get_login_url())

    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    credential = request.POST.get("credential", "")
    if not credential:
        messages.error(request, "Google authentication failed.")
        return redirect(get_login_url())

    client_id = get_client_id()
    if not client_id:
        messages.error(request, "Google Sign-In is not configured.")
        return redirect(get_login_url())

    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id,
        )
    except ValueError as e:
        logger.warning("Google token verification failed: %s", e)
        messages.error(request, "Invalid Google token.")
        return redirect(get_login_url())

    email = idinfo.get("email", "").lower()
    name = idinfo.get("name", "")

    if not email:
        messages.error(request, "Google account has no email.")
        return redirect(get_login_url())

    # Find or create user
    created = False
    email_field = User.USERNAME_FIELD if User.USERNAME_FIELD == "email" else "email"
    user = User.objects.filter(**{email_field: email}).first()

    if not user:
        user = _create_user(email, name)
        created = True
    else:
        _update_existing_user(user)

    login(request, user)

    # Project-specific callback hook
    callback = getattr(settings, "GSI_CALLBACK", None)
    if callback:
        if isinstance(callback, str):
            from django.utils.module_loading import import_string
            callback = import_string(callback)
        callback(request, user, created)

    next_url = request.POST.get("next", "")
    if next_url:
        return redirect(next_url)
    return redirect(get_login_redirect_url())


def _create_user(email, name):
    """Create a new user from Google profile info."""
    kwargs = {"email": email}

    # Set username field
    username_field = User.USERNAME_FIELD
    if username_field == "email":
        kwargs["username"] = email
    else:
        kwargs[username_field] = email

    # Set name fields
    if hasattr(User, "full_name"):
        kwargs["full_name"] = name
    else:
        parts = name.split(" ", 1) if name else ["", ""]
        if hasattr(User, "first_name"):
            kwargs["first_name"] = parts[0]
        if hasattr(User, "last_name"):
            kwargs["last_name"] = parts[1] if len(parts) > 1 else ""

    # Mark email as confirmed if field exists
    if hasattr(User, "email_confirmed"):
        kwargs["email_confirmed"] = True

    user = User(**kwargs)
    user.set_unusable_password()
    user.save()
    return user


def _update_existing_user(user):
    """Update existing user after Google login (e.g. confirm email)."""
    if hasattr(user, "email_confirmed") and not user.email_confirmed:
        user.email_confirmed = True
        user.save(update_fields=["email_confirmed"])
