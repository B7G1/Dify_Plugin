"""Read-only SQL query tool for the configured MySQL or PostgreSQL provider."""

import logging
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.database import execute_read_only_query
from utils.errors import DatabaseQueryError
from utils.result_formatter import error_response, success_response
from utils.validation import validate_connection_config, validate_tool_parameters


logger = logging.getLogger(__name__)


class DbQueryExtendedTool(Tool):
    """Execute one validated read-only SQL request."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        logger.info("Tool invocation started")
        database_type = None
        max_rows = 100
        try:
            parameters = validate_tool_parameters(tool_parameters)
            max_rows = parameters["max_rows"]
            credentials = validate_connection_config(self.runtime.credentials)
            database_type = credentials["database_type"]
            result = execute_read_only_query(
                credentials,
                parameters["sql"],
                parameters["max_rows"],
                parameters["timeout_seconds"],
            )
            response = success_response(database_type, result)
        except DatabaseQueryError as exc:
            logger.warning("Tool invocation rejected or failed: %s", exc)
            yield self.create_json_message(error_response(exc, database_type=database_type, max_rows=max_rows))
            return
        except Exception as exc:
            logger.error("Tool invocation failed: %s", exc.__class__.__name__)
            yield self.create_json_message(error_response(exc, database_type=database_type, max_rows=max_rows))
            return

        logger.info("Tool invocation completed; rows=%s truncated=%s", response["row_count"], response["truncated"])
        yield self.create_json_message(response)
