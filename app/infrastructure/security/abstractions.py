from abc import ABC, abstractmethod


class SecurityContext:
    def __init__(self, user_id: str, tenant_id: str, roles: list[str]):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.roles = roles

class IAuthenticator(ABC):
    @abstractmethod
    def authenticate(self, token: str) -> SecurityContext:
        pass

class IAuthorizationPolicy(ABC):
    @abstractmethod
    def is_authorized(self, context: SecurityContext, action: str, resource: str) -> bool:
        pass

class ISecretManager(ABC):
    @abstractmethod
    def get_secret(self, key: str) -> str:
        pass
