from django import template
from django.utils.safestring import mark_safe

from gsi.conf import get_client_id

register = template.Library()


@register.simple_tag(takes_context=True)
def google_signin_button(context, text="signin_with", divider_text="or"):
    """
    Render Google Sign-In button with CSRF-safe JavaScript callback.

    Usage:
        {% load gsi_tags %}
        {% google_signin_button %}
        {% google_signin_button text="signup_with" divider_text="or" %}
    """
    client_id = get_client_id()
    if not client_id:
        return ""

    request = context.get("request")
    csrf_token = context.get("csrf_token", "")

    html = """
<div style="margin:1rem 0;text-align:center">
  <div style="border-top:1px solid #ddd;margin:1rem 0;position:relative">
    <span style="background:#fff;padding:0 0.75rem;position:relative;top:-0.75rem;color:#888;font-size:0.85rem">%(divider)s</span>
  </div>
  <div id="g_id_onload"
       data-client_id="%(client_id)s"
       data-callback="handleGSIResponse"
       data-auto_prompt="false">
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
<script>
function handleGSIResponse(response) {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/accounts/google/callback/';
    var csrf = document.createElement('input');
    csrf.type = 'hidden'; csrf.name = 'csrfmiddlewaretoken';
    csrf.value = '%(csrf)s';
    form.appendChild(csrf);
    var cred = document.createElement('input');
    cred.type = 'hidden'; cred.name = 'credential';
    cred.value = response.credential;
    form.appendChild(cred);
    var next = new URLSearchParams(window.location.search).get('next');
    if (next) {
        var n = document.createElement('input');
        n.type = 'hidden'; n.name = 'next'; n.value = next;
        form.appendChild(n);
    }
    document.body.appendChild(form);
    form.submit();
}
</script>
""" % {
        "client_id": client_id,
        "text": text,
        "divider": divider_text,
        "csrf": csrf_token,
    }

    return mark_safe(html)
