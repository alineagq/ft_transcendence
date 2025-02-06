from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from auth.domain.entities import UserEntity
from auth.domain.exceptions import AuthenticationError
from auth.infraestructure.jwt_utils import generate_jwt

class AuthUseCase:
    """Caso de uso para autenticação"""

    @staticmethod
    def register(username, password):
        """Registra um novo usuário"""
        if not username  or not password:
            raise ValidationError("Todos os campos são obrigatórios.")

        if User.objects.filter(username=username).exists():
            raise ValidationError("Nome de usuário já está em uso.")

        try:
            user = User.objects.create_user(username=username, password=password)
            return UserEntity(user.id, user.username)
        except IntegrityError:
            raise ValidationError("Erro ao criar usuário. Tente novamente.")

    @staticmethod
    def login(username, password):
        """Autentica um usuário"""
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationError("Credenciais inválidas")

        user_entity = UserEntity(user.id, user.username)
        access_token, refresh_token = generate_jwt(user_entity)
        return access_token, refresh_token
