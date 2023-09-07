from django.shortcuts import redirect
import logging


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifica si el nombre de usuario en la sesión está vacío
        username = request.session.get('username', '')
        if not username:
            # Redirige al usuario a la vista de logout (ajusta la URL según sea necesario)
            return redirect('logout')  # Reemplaza 'logout' con el nombre de la vista de logout

        response = self.get_response(request)
        return response

class PrintClientIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip = get_client_ip(request)
        print("IP:", client_ip, " Session:", request.session.get('user_id', ''), " - Nombre:", request.session.get('username', ''))

        response = self.get_response(request)
        return response

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
