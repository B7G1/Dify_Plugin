"""Provider shell for the legacy inline-credential Tool."""

from dify_plugin import ToolProvider


class LegacyDatabaseQueryProvider(ToolProvider):
    """The legacy Tool owns credentials per invocation, so there is nothing to persist."""

    def _validate_credentials(self, credentials: dict) -> None:
        del credentials
