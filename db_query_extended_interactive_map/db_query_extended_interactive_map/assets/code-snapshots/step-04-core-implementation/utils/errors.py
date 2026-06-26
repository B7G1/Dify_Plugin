"""Safe, user-facing error types for the database query plugin."""


class DatabaseQueryError(Exception):
    """Base error whose message is suitable for Dify users."""


class ParameterValidationError(DatabaseQueryError):
    """A required or constrained parameter is invalid."""


class UnsupportedDatabaseTypeError(DatabaseQueryError):
    """The selected database engine is not enabled."""


class ConnectionFailedError(DatabaseQueryError):
    """The configured database endpoint cannot be reached or verified."""


class SqlExecutionError(DatabaseQueryError):
    """Reserved for the real SQL execution phase."""


class QueryTimeoutError(DatabaseQueryError):
    """Reserved for database query timeout handling."""


class ResultTooLargeError(DatabaseQueryError):
    """Reserved for result-size limit handling."""


class ReadOnlyViolationError(DatabaseQueryError):
    """The submitted SQL is not allowed in read-only mode."""
