# django-gsi

Minimal Google Sign-In for Django. One Google Client ID, works on any Django project.

## Installation

```bash
pip install git+https://github.com/akarca/django-google-auth.git
```

## Setup (3 steps)

### 1. Settings

```python
INSTALLED_APPS = [
    ...
    "gsi",
]

TEMPLATES = [{
    "OPTIONS": {
        "context_processors": [
            ...
            "gsi.context_processors.google_client_id",
        ],
    },
}]

GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
```

### 2. URLs

```python
from django.urls import include, path

urlpatterns = [
    ...
    path("", include("gsi.urls")),
]
```

### 3. Template

```html
{% load gsi_tags %}

<!-- In your login form -->
{% google_signin_button %}

<!-- In your register form -->
{% google_signin_button text="signup_with" %}
```

That's it. Users who sign in with Google are automatically logged in (existing account) or registered (new account).

## How It Works

1. User clicks the Google Sign-In button
2. Google popup opens, user authorizes
3. Google returns a JWT credential to the JavaScript callback
4. JavaScript submits the credential to `/accounts/google/callback/` with CSRF token
5. Backend verifies the JWT using `google-auth` library
6. If email matches existing user → login
7. If new email → create user with `unusable_password`, `email_confirmed=True`
8. Redirect to `LOGIN_REDIRECT_URL` or `?next=` parameter

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `GOOGLE_CLIENT_ID` | `""` | Google OAuth Client ID (required) |
| `LOGIN_REDIRECT_URL` | `"/"` | Where to redirect after login |
| `LOGIN_URL` | `"/accounts/login/"` | Where to redirect on error |
| `GSI_CALLBACK` | `None` | Post-login hook (see below) |

## Post-Login Hook

For project-specific logic after Google login (cart migration, analytics, etc.):

```python
# settings.py
GSI_CALLBACK = "myapp.auth.on_google_login"

# myapp/auth.py
def on_google_login(request, user, created):
    """Called after successful Google login/register."""
    if created:
        # New user — send welcome email, etc.
        pass
    # Migrate cart, set session data, etc.
```

## User Model Compatibility

Works with any Django User model:
- `USERNAME_FIELD = "email"` → uses email as username
- `USERNAME_FIELD = "username"` → sets username to email
- Has `full_name` field → sets from Google profile name
- Has `first_name`/`last_name` → splits Google name
- Has `email_confirmed` field → sets to `True`

## Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (e.g. "Yuix Networks Inc")
3. APIs & Services → Credentials → Create OAuth 2.0 Client ID
4. Application type: Web application
5. Authorized JavaScript origins: add all your domains
   - `https://nameocean.net`
   - `https://ipaddress.world`
   - `https://fenerbahce.fan`
6. Copy the Client ID to your Django settings

One Client ID works for all your sites.

## License

MIT
