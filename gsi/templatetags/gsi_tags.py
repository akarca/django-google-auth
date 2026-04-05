from django import template
from django.utils.safestring import mark_safe

from gsi.conf import get_client_id

register = template.Library()


@register.simple_tag(takes_context=True)
def google_signin_button(context, text="signin_with", divider_text="or"):
    """
    Render Google Sign-In button using redirect mode.

    Usage:
        {% load gsi_tags %}
        {% google_signin_button %}
        {% google_signin_button text="signup_with" divider_text="or" %}
    """
    client_id = get_client_id()
    if not client_id:
        return ""

    # Build absolute callback URL from request
    request = context.get("request")
    if request:
        scheme = "https" if request.is_secure() else "http"
        host = request.get_host()
        callback_url = "%s://%s/accounts/google/callback/" % (scheme, host)
    else:
        callback_url = "/accounts/google/callback/"

    html = """
<div style="margin:1rem 0;text-align:center">
  <div style="border-top:1px solid #ddd;margin:1rem 0;position:relative">
    <span style="background:#fff;padding:0 0.75rem;position:relative;top:-0.75rem;color:#888;font-size:0.85rem">%(divider)s</span>
  </div>
  <div id="g_id_onload"
       data-client_id="%(client_id)s"
       data-login_uri="%(callback_url)s"
       data-auto_prompt="false"
       data-ux_mode="redirect">
  </div>
  <div class="g_id_signin"
       data-type="standard"
       data-shape="rectangular"
       data-theme="outline"
       data-text="%(text)s"
       data-size="large"
       data-logo_alignment="left">
  </div>
</div>
<script src="https://accounts.google.com/gsi/client" async defer></script>
""" % {
        "client_id": client_id,
        "text": text,
        "divider": divider_text,
        "callback_url": callback_url,
    }

    return mark_safe(html)
