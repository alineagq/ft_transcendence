# auth/infraestructure/jwt_utils.py
import base64
import json
import hmac
import hashlib
import datetime
from django.conf import settings
from auth.domain.exceptions import TokenError
from auth.domain.entities import UserEntity  # Para type hints, se necessário


class JWTService:
    """Serviço para operações com JWT."""

    @staticmethod
    def base64url_encode(data: bytes) -> str:
        """Codifica dados em Base64 URL-safe."""
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    @staticmethod
    def base64url_decode(data: str) -> bytes:
        """Decodifica dados em Base64 URL-safe."""
        padding = "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + padding)

    @staticmethod
    def _create_token(header: dict, payload: dict, secret_key: bytes) -> str:
        """Cria um token JWT a partir do header e payload."""
        encoded_header = JWTService.base64url_encode(json.dumps(header).encode("utf-8"))
        encoded_payload = JWTService.base64url_encode(json.dumps(payload).encode("utf-8"))
        signature = hmac.new(
            secret_key,
            f"{encoded_header}.{encoded_payload}".encode("utf-8"),
            hashlib.sha256,
        ).digest()
        encoded_signature = JWTService.base64url_encode(signature)
        return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

    @classmethod
    def generate_tokens(cls, user: UserEntity) -> tuple[str, str]:
        """Gera tokens JWT (access e refresh) para o usuário."""
        secret_key = settings.SECRET_KEY.encode("utf-8")
        header = {"alg": "HS256", "typ": "JWT"}
        access_payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": (datetime.datetime.utcnow() + datetime.timedelta(minutes=30)).timestamp(),
        }
        refresh_payload = {
            "user_id": user.id,
            "exp": (datetime.datetime.utcnow() + datetime.timedelta(days=7)).timestamp(),
        }
        access_token = cls._create_token(header, access_payload, secret_key)
        refresh_token = cls._create_token(header, refresh_payload, secret_key)
        return access_token, refresh_token

    @classmethod
    def decode(cls, token: str) -> dict:
        """Decodifica e valida um JWT."""
        secret_key = settings.SECRET_KEY.encode("utf-8")
        try:
            encoded_header, encoded_payload, encoded_signature = token.split(".")
            expected_signature = hmac.new(
                secret_key,
                f"{encoded_header}.{encoded_payload}".encode("utf-8"),
                hashlib.sha256,
            ).digest()
            if not hmac.compare_digest(cls.base64url_encode(expected_signature), encoded_signature):
                raise TokenError("Assinatura inválida")
            payload_bytes = cls.base64url_decode(encoded_payload)
            payload = json.loads(payload_bytes.decode("utf-8"))
            if payload.get("exp", 0) < datetime.datetime.utcnow().timestamp():
                raise TokenError("Token expirado")
            return payload
        except Exception as e:
            raise TokenError("Token inválido") from e

    @classmethod
    def decode_without_verification(cls, token: str) -> tuple[dict, dict]:
        """Decodifica um JWT sem verificar assinatura e expiração."""
        try:
            encoded_header, encoded_payload, _ = token.split(".")
            header_bytes = cls.base64url_decode(encoded_header)
            payload_bytes = cls.base64url_decode(encoded_payload)
            header = json.loads(header_bytes.decode("utf-8"))
            payload = json.loads(payload_bytes.decode("utf-8"))
            return header, payload
        except Exception as e:
            raise TokenError("Falha ao decodificar token sem verificação") from e
