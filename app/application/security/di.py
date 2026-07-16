from typing import TYPE_CHECKING
import os

from app.domain.security.interfaces import IHasher, IEncryptor, ITokenGenerator, IIdentityProvider, IAuthenticationService, IPolicyRepository, IPolicyEngine, IAuditSink, IAuditPublisher
from app.domain.security.config import SecurityConfig
from app.infrastructure.security.hashers import BcryptHasher
from app.infrastructure.security.encryptors import AES256GCMEncryptor
from app.infrastructure.security.tokens import CSPRNGTokenGenerator
from app.application.security.crypto_service import CryptographyService
from app.config import Settings

if TYPE_CHECKING:
    from app.bootstrap.container import Container

def register_security_dependencies(container: "Container") -> None:
    """Registers security-related dependencies in the DI container."""
    
    # Register SecurityConfig
    def build_security_config(c: "Container") -> SecurityConfig:
        settings = c.resolve(Settings)
        return SecurityConfig.from_settings(
            key_base64=settings.encryption_key_base64,
            rounds=settings.bcrypt_rounds,
            jwt_secret=settings.jwt_secret
        )
        
    container.register_factory(SecurityConfig, build_security_config)
    
    # Register Hashers
    def build_hasher(c: "Container") -> IHasher:
        config = c.resolve(SecurityConfig)
        return BcryptHasher(rounds=config.bcrypt_rounds)
        
    container.register_factory(IHasher, build_hasher)
    
    # Register Token Generator
    def build_token_generator(c: "Container") -> ITokenGenerator:
        config = c.resolve(SecurityConfig)
        return CSPRNGTokenGenerator(token_length_bytes=config.token_length_bytes)
        
    container.register_factory(ITokenGenerator, build_token_generator)
    
    # Register Encryptor 
    def build_encryptor(c: "Container") -> IEncryptor:
        config = c.resolve(SecurityConfig)
        return AES256GCMEncryptor(key=config.encryption_key)
        
    container.register_factory(IEncryptor, build_encryptor)
    
    # Register CryptographyService
    def build_crypto_service(c: "Container") -> CryptographyService:
        return CryptographyService(
            hasher=c.resolve(IHasher),
            encryptor=c.resolve(IEncryptor),
            token_generator=c.resolve(ITokenGenerator)
        )
        
    container.register_factory(CryptographyService, build_crypto_service)
    
    # ── Identity Providers & Authentication ──

    from app.domain.identity.interfaces import IAPIKeyRepository
    from app.infrastructure.persistence.memory.api_key_repository import InMemoryAPIKeyRepository
    from app.infrastructure.security.policy_repository import InMemoryPolicyRepository
    from app.application.security.auth_service import AuthenticationService
    from app.application.security.authz_service import AuthorizationService

    from app.infrastructure.security.providers.jwt_provider import JWTIdentityProvider
    from app.infrastructure.security.providers.api_key_provider import APIKeyIdentityProvider
    from app.infrastructure.security.audit import InMemoryAuditSink, EventBusAuditPublisher, AuditSubscriber
    from app.shared.events.bus import EventBus
    
    # --- Audit & Security Observability (Wave-4 M5) ---
    container.register_singleton(IAuditSink, InMemoryAuditSink())
    
    def build_audit_publisher(c: "Container") -> IAuditPublisher:
        return EventBusAuditPublisher(event_bus=c.resolve(EventBus))
        
    container.register_factory(IAuditPublisher, build_audit_publisher)
    
    def build_audit_subscriber(c: "Container") -> AuditSubscriber:
        return AuditSubscriber(
            event_bus=c.resolve(EventBus),
            sink=c.resolve(IAuditSink)
        )
        
    container.register_factory(AuditSubscriber, build_audit_subscriber)

    # Register API Key Repository
    container.register_singleton(IAPIKeyRepository, InMemoryAPIKeyRepository())

    def build_jwt_provider(c: "Container") -> IIdentityProvider:
        return JWTIdentityProvider(config=c.resolve(SecurityConfig))

    def build_api_key_provider(c: "Container") -> IIdentityProvider:
        return APIKeyIdentityProvider(
            repo=c.resolve(IAPIKeyRepository),
            hasher=c.resolve(IHasher)
        )

    container.register_factory(JWTIdentityProvider, build_jwt_provider)
    container.register_factory(APIKeyIdentityProvider, build_api_key_provider)

    def build_auth_service(c: "Container") -> IAuthenticationService:
        providers = [
            c.resolve(JWTIdentityProvider),
            c.resolve(APIKeyIdentityProvider)
        ]
        return AuthenticationService(
            providers=providers, 
            audit_publisher=c.resolve(IAuditPublisher)
        )

    container.register_factory(IAuthenticationService, build_auth_service)
    
    # --- Authorization (Wave-4 M3) ---
    container.register_singleton(IPolicyRepository, InMemoryPolicyRepository())
    
    def build_authz_service(c: "Container") -> IPolicyEngine:
        return AuthorizationService(
            policy_repo=c.resolve(IPolicyRepository),
            audit_publisher=c.resolve(IAuditPublisher)
        )
        
    container.register_factory(IPolicyEngine, build_authz_service)
