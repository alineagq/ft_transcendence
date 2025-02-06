class AuthenticationError(Exception):
    """Erro de autenticação (Credenciais inválidas)"""
    pass

class TokenError(Exception):
    """Erro relacionado ao JWT (inválido ou expirado)"""
    pass
