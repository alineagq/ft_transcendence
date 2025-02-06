from django.http import JsonResponse
from auth.usecases.auth_usecase import AuthUseCase
from auth.domain.exceptions import TokenError

class JWTAuthenticationMiddleware:
    """Middleware para autenticar usuários com JWT"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = AuthUseCase.refresh_token(token)
                request.user_id = payload["user_id"]
            except TokenError:
                return JsonResponse({"error": "Token inválido ou expirado"}, status=401)

        return self.get_response(request)
