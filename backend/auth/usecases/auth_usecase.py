# auth/usecases/auth_usecase.py
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from auth.domain.entities import UserEntity
from auth.domain.exceptions import AuthenticationError
from auth.infraestructure.jwt_utils import JWTService


class AuthUseCase:
    """Caso de uso para autenticação."""

    @staticmethod
    def register(username: str, password: str) -> UserEntity:
        """Registra um novo usuário."""
        if not username or not password:
            raise ValidationError("Todos os campos são obrigatórios.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Nome de usuário já está em uso.")
        try:
            user = User.objects.create_user(username=username, password=password)
            return UserEntity(user.id, user.username)
        except IntegrityError:
            raise ValidationError("Erro ao criar usuário. Tente novamente.")

    @staticmethod
    def login(username: str, password: str) -> tuple[str, str]:
        """Autentica um usuário e gera tokens JWT."""
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationError("Credenciais inválidas")
        user_entity = UserEntity(user.id, user.username)
        access_token, refresh_token = JWTService.generate_tokens(user_entity)
        return access_token, refresh_token

    @staticmethod
    def login_with_auth0(payload: dict) -> tuple[str, str]:
        """Autentica ou cria um usuário usando os dados do Auth0."""
        auth0_id = payload.get("sub")
        if not auth0_id:
            raise AuthenticationError("ID do Auth0 não encontrado no token")
        try:
            user = User.objects.get(username=auth0_id)
        except User.DoesNotExist:
            random_password = User.objects.make_random_password()
            user = User.objects.create_user(username=auth0_id, password=random_password)
            email = payload.get("email")
            if email:
                user.email = email
                user.save()
        user_entity = UserEntity(user.id, user.username)
        access_token, refresh_token = JWTService.generate_tokens(user_entity)
        return access_token, refresh_token

    @staticmethod
    def refresh_token(refresh_token: str) -> str:
        """Renova o access token a partir do refresh token.
        
        Este método deve implementar a lógica de verificação do refresh token.
        Para simplicidade, aqui não é implementado.
        """
        raise NotImplementedError("Refresh token não implementado")
