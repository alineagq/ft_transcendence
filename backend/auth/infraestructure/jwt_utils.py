import base64
import json
import hmac
import hashlib
import datetime
from django.conf import settings
from auth.domain.exceptions import TokenError
from auth.domain.entities import UserEntity

def base64url_encode(data):
    """Codifica em Base64 URL-safe."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def base64url_decode(data):
    """Decodifica Base64 URL-safe."""
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def generate_jwt(user):
    """Gera tokens JWT"""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": (datetime.datetime.utcnow() + datetime.timedelta(minutes=30)).timestamp()
    }

    refresh_payload = {
        "user_id": user.id,
        "exp": (datetime.datetime.utcnow() + datetime.timedelta(days=7)).timestamp()
    }

    secret_key = settings.SECRET_KEY.encode()

    encoded_header = base64url_encode(json.dumps(header).encode())
    encoded_payload = base64url_encode(json.dumps(payload).encode())
    encoded_refresh_payload = base64url_encode(json.dumps(refresh_payload).encode())

    signature = hmac.new(secret_key, f"{encoded_header}.{encoded_payload}".encode(), hashlib.sha256).digest()
    refresh_signature = hmac.new(secret_key, f"{encoded_header}.{encoded_refresh_payload}".encode(), hashlib.sha256).digest()

    access_token = f"{encoded_header}.{encoded_payload}.{base64url_encode(signature)}"
    refresh_token = f"{encoded_header}.{encoded_refresh_payload}.{base64url_encode(refresh_signature)}"

    return access_token, refresh_token

def decode_jwt(token):
    """Decodifica e valida um JWT"""
    try:
        secret_key = settings.SECRET_KEY.encode()
        encoded_header, encoded_payload, encoded_signature = token.split(".")

        expected_signature = hmac.new(secret_key, f"{encoded_header}.{encoded_payload}".encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(base64url_encode(expected_signature), encoded_signature):
            raise TokenError("Assinatura inválida")

        payload = json.loads(base64url_decode(encoded_payload))
        if payload["exp"] < datetime.datetime.utcnow().timestamp():
            raise TokenError("Token expirado")

        return payload
    except Exception:
        raise TokenError("Token inválido")

