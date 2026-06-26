"""Read-only SQL query tool for the configured MySQL or PostgreSQL provider."""

import logging
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.database import execute_read_only_query
from utils.errors import DatabaseQueryError
from utils.validation import validate_connection_config, validate_tool_parameters


logger = logging.getLogger(__name__)


class DbQueryExtendedTool(Tool):
    """Execute one validated read-only SQL request."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        logger.info("Tool invocation started")
        try:
            parameters = validate_tool_parameters(tool_parameters)
            credentials = validate_connection_config(self.runtime.credentials)
            result = execute_read_only_query(
                credentials,
                parameters["sql"],
                parameters["max_rows"],
                parameters["timeout"],
            )
        except DatabaseQueryError as exc:
            logger.warning("Tool invocation rejected or failed: %s", exc)
            raise ValueError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Tool invocation failed: %s", exc.__class__.__name__)
            raise ValueError("The query request could not be completed.") from exc

        logger.info("Tool invocation completed; rows=%s truncated=%s", result["row_count"], result["truncated"])
        yield self.create_json_message(result)
