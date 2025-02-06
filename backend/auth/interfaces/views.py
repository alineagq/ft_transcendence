from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from auth.usecases.auth_usecase import AuthUseCase
from auth.domain.exceptions import AuthenticationError, TokenError
from django.core.exceptions import ValidationError

@csrf_exempt
def register_view(request):
    """Cadastro de novo usuário"""
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    try:
        user = AuthUseCase.register(username, password)
        return JsonResponse({"message": "Usuário registrado com sucesso", "username": user.username}, status=201)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def login_view(request):
    """Login e geração de JWT"""
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    data = json.loads(request.body)
    username, password = data.get("username"), data.get("password")

    try:
        access_token, refresh_token = AuthUseCase.login(username, password)
        response = JsonResponse({"access_token": access_token})
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")
        return response
    except AuthenticationError as e:
        return JsonResponse({"error": str(e)}, status=401)

@csrf_exempt
def refresh_token_view(request):
    """Renovação do Access Token"""
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        return JsonResponse({"error": "Refresh token não encontrado"}, status=401)

    try:
        access_token = AuthUseCase.refresh_token(refresh_token)
        return JsonResponse({"access_token": access_token})
    except TokenError as e:
        return JsonResponse({"error": str(e)}, status=401)

@csrf_exempt
def logout_view(request):
    """Logout"""
    response = JsonResponse({"message": "Logout realizado com sucesso"})
    response.delete_cookie("refresh_token")
    return response