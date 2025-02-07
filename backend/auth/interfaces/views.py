import json
import urllib.request
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from auth.usecases.auth_usecase import AuthUseCase
from auth.domain.exceptions import AuthenticationError, TokenError
from auth.infraestructure import jwt_utils


def post_json(url: str, data: dict) -> str:
    """Helper para enviar requisição POST com payload JSON."""
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8")


@csrf_exempt
def register_view(request):
    """Cadastro de novo usuário."""
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        user = AuthUseCase.register(username, password)
        return JsonResponse(
            {"message": "Usuário registrado com sucesso", "username": user.username},
            status=201,
        )
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def login_view(request):
    """Login e geração de JWT."""
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        access_token, refresh_token = AuthUseCase.login(username, password)
        response = JsonResponse({"access_token": access_token})
        response.set_cookie(
            "refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax"
        )
        return response
    except AuthenticationError as e:
        return JsonResponse({"error": str(e)}, status=401)


@csrf_exempt
def refresh_token_view(request):
    """Renovação do Access Token."""
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
    """Logout."""
    response = JsonResponse({"message": "Logout realizado com sucesso"})
    response.delete_cookie("refresh_token")
    return response


@csrf_exempt
def auth0_callback_view(request):
    """Callback do Auth0."""
    code = request.GET.get("code")
    if not code:
        return HttpResponseBadRequest("Código não fornecido")

    token_url = "https://YOUR_AUTH0_DOMAIN/oauth/token"
    payload_data = {
        "grant_type": "authorization_code",
        "client_id": "YOUR_AUTH0_CLIENT_ID",
        "client_secret": "YOUR_AUTH0_CLIENT_SECRET",
        "code": code,
        "redirect_uri": "YOUR_CALLBACK_URL",
    }
    try:
        token_response_str = post_json(token_url, payload_data)
    except Exception as e:
        return JsonResponse({"error": "Falha na troca do token: " + str(e)}, status=400)

    tokens = json.loads(token_response_str)
    id_token = tokens.get("id_token")
    if not id_token:
        return JsonResponse({"error": "id_token não encontrado"}, status=400)

    try:
        # Decodifica o id_token sem verificar assinatura/expiração para extrair header e payload
        header, payload = jwt_utils.JWTService.decode_without_verification(id_token)
    except Exception as e:
        return JsonResponse({"error": "Erro ao decodificar o token: " + str(e)}, status=400)

    if payload.get("aud") != "YOUR_AUTH0_CLIENT_ID" or payload.get("iss") != "https://YOUR_AUTH0_DOMAIN/":
        return JsonResponse({"error": "Token inválido"}, status=400)

    try:
        access_token, refresh_token = AuthUseCase.login_with_auth0(payload)
    except Exception as e:
        return JsonResponse({"error": "Erro na autenticação com Auth0: " + str(e)}, status=400)

    response = JsonResponse({"access_token": access_token})
    response.set_cookie(
        "refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax"
    )
    return response
