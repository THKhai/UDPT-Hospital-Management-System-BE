from dependency_injector import containers, providers
from config.database import get_db
from src.repositories.auth_repository import AuthRepository
from src.services.auth_service import AuthService
class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the application.
    This container holds all the providers for the application.
    """
    #database
    db_main =providers.Resource(get_db)

    # Repositories
    auth_repository = providers.Factory(
        AuthRepository,
        db=db_main
    )
    # Services
    auth_service = providers.Factory(
        AuthService,
        auth_repository=auth_repository
    )