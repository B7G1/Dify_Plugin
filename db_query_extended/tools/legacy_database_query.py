"""Legacy-compatible inline-credential database query Tool."""

import logging
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.database import execute_read_only_query
from utils.errors import DatabaseQueryError
from utils.legacy import run_legacy_query


logger = logging.getLogger(__name__)
class LegacyDatabaseQueryTool(Tool):
    """Preserve the original external contract while reusing the secure core."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            payload = run_legacy_query(tool_parameters, execute_read_only_query)
        except DatabaseQueryError as exc:
            logger.warning("Legacy Tool rejected request: %s", exc.__class__.__name__)
            yield self.create_json_message({"error": {"type": exc.__class__.__name__, "message": str(exc)}})
            return
        except Exception as exc:
            logger.error("Legacy Tool failed: %s", exc.__class__.__name__)
            yield self.create_json_message({"error": {"type": "DatabaseQueryError", "message": "The query request could not be completed."}})
            return
        if isinstance(payload, str):
            yield self.create_text_message(payload)
        else:
            if isinstance(payload, dict) and isinstance(payload.get("records"), list):
                yield self.create_variable_message("result", payload)
            yield self.create_json_message(payload)
