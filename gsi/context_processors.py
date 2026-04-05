from .conf import get_client_id


def google_client_id(request):
    return {"GOOGLE_CLIENT_ID": get_client_id()}
