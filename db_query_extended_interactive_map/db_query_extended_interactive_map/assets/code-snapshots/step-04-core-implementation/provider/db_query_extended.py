"""Provider configuration validation for db_query_extended."""

import logging
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.database import verify_database_connection
from utils.errors import DatabaseQueryError
from utils.validation import validate_connection_config


logger = logging.getLogger(__name__)


class DbQueryExtendedProvider(ToolProvider):
    """Validate configuration and database authentication; never executes user SQL."""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        logger.info("Provider credential validation started")
        try:
            config = validate_connection_config(credentials)
            verify_database_connection(config)
        except DatabaseQueryError as exc:
            logger.warning("Provider credential validation failed: %s", exc)
            raise ToolProviderCredentialValidationError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Provider credential validation failed: %s", exc.__class__.__name__)
            raise ToolProviderCredentialValidationError("Database connection configuration could not be validated.") from exc
        logger.info("Provider credential validation completed for database_type=%s", config["database_type"])
