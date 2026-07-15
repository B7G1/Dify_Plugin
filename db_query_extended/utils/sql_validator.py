"""Read-only SQL validation with SQL-aware lexical analysis.

The plugin is distributed from an offline dependency set.  Until a dedicated
AST parser is added to the offline wheels, this module uses a conservative SQL
lexer that understands comments, strings, quoted identifiers, PostgreSQL
dollar-quoted strings, and statement separators.  The validator rejects anything
ambiguous instead of trying to be clever.  The current public contract accepts
only SELECT and WITH statements; EXPLAIN and adapter-specific commands are kept
out of the tool surface until each database behavior is explicitly verified.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from utils.errors import ParameterValidationError, ReadOnlyViolationError


MAX_SQL_LENGTH = 100_000

ALLOWED_START_KEYWORDS = {"SELECT", "WITH"}
LEGACY_ALLOWED_START_KEYWORDS = {"SELECT"}
FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "CALL",
    "EXEC",
    "EXECUTE",
    "MERGE",
    "COPY",
    "LOAD",
    "GRANT",
    "REVOKE",
    "REPLACE",
    "UPSERT",
    "VACUUM",
    "ANALYZE",
    "LOCK",
    "UNLOCK",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT",
    "SET",
    "RESET",
    "USE",
    "INTO",
}

READ_ONLY_ERROR = (
    "Only one read-only SELECT or WITH statement is allowed. "
    "DDL, DML, procedure calls, file operations, comments-based bypasses, and multiple statements are blocked."
)
LEGACY_SELECT_ERROR = "Only one SELECT statement is allowed for the legacy tool."


@dataclass(frozen=True)
class SqlValidationResult:
    """Normalized validation result for downstream execution."""

    sql: str
    statement_type: str
    tokens: tuple[str, ...]


class ReadOnlyValidator:
    """Validate that a SQL statement is a single conservative read-only query."""

    def validate(self, sql: str) -> SqlValidationResult:
        if sql is None or not str(sql).strip():
            raise ParameterValidationError("SQL must not be empty.")

        normalized_sql = str(sql).strip()
        if len(normalized_sql) > MAX_SQL_LENGTH:
            raise ParameterValidationError(f"SQL length must not exceed {MAX_SQL_LENGTH} characters.")

        tokens, semicolon_count = _lex_sql(normalized_sql)
        if not tokens:
            raise ParameterValidationError("SQL must not be empty.")
        if semicolon_count > 0:
            # Reject all semicolons. This is stricter than allowing a trailing
            # semicolon, but it closes semicolon-injection and multi-statement
            # ambiguity uniformly across MySQL and PostgreSQL drivers.
            raise ReadOnlyViolationError(READ_ONLY_ERROR)

        statement_type = tokens[0]
        if statement_type not in ALLOWED_START_KEYWORDS:
            raise ReadOnlyViolationError(READ_ONLY_ERROR)

        forbidden = FORBIDDEN_KEYWORDS.intersection(tokens)
        if forbidden:
            raise ReadOnlyViolationError(READ_ONLY_ERROR)

        if statement_type == "WITH":
            self._validate_with(tokens)

        return SqlValidationResult(sql=normalized_sql, statement_type=statement_type, tokens=tuple(tokens))

    def _validate_with(self, tokens: list[str]) -> None:
        # WITH can prefix SELECT or write statements.  Since write tokens are
        # already rejected globally, require that a SELECT exists after WITH.
        if "SELECT" not in tokens[1:]:
            raise ReadOnlyViolationError(READ_ONLY_ERROR)


class LegacySingleSelectValidator:
    """Preserve the original Tool's single-SELECT boundary before execution."""

    def validate(self, sql: str) -> SqlValidationResult:
        if sql is None or not str(sql).strip():
            raise ParameterValidationError("SQL must not be empty.")

        normalized_sql = str(sql).strip()
        if len(normalized_sql) > MAX_SQL_LENGTH:
            raise ParameterValidationError(f"SQL length must not exceed {MAX_SQL_LENGTH} characters.")

        # Original sqlparse handling accepts one terminal semicolon. Retain that
        # compatibility without allowing a separator anywhere else.
        token_sql = normalized_sql[:-1].rstrip() if normalized_sql.endswith(";") else normalized_sql
        tokens, semicolon_count = _lex_sql(token_sql)
        if not tokens or semicolon_count or tokens[0] not in LEGACY_ALLOWED_START_KEYWORDS:
            raise ReadOnlyViolationError(LEGACY_SELECT_ERROR)
        if FORBIDDEN_KEYWORDS.intersection(tokens):
            raise ReadOnlyViolationError(LEGACY_SELECT_ERROR)
        return SqlValidationResult(sql=normalized_sql, statement_type="SELECT", tokens=tuple(tokens))


def _lex_sql(sql: str) -> tuple[list[str], int]:
    """Return uppercase SQL word tokens outside strings/comments and semicolon count."""
    tokens: list[str] = []
    semicolon_count = 0
    i = 0
    length = len(sql)

    while i < length:
        char = sql[i]
        nxt = sql[i + 1] if i + 1 < length else ""

        if char.isspace():
            i += 1
            continue

        if char == "-" and nxt == "-":
            i = _skip_line_comment(sql, i + 2)
            continue

        if char == "#":
            i = _skip_line_comment(sql, i + 1)
            continue

        if char == "/" and nxt == "*":
            i = _skip_block_comment(sql, i + 2)
            continue

        if char == "'":
            i = _skip_single_quoted(sql, i + 1)
            continue

        if char == '"':
            i = _skip_double_quoted(sql, i + 1)
            continue

        if char == "`":
            i = _skip_backtick_quoted(sql, i + 1)
            continue

        if char == "$":
            dollar_end = _try_skip_dollar_quoted(sql, i)
            if dollar_end is not None:
                i = dollar_end
                continue

        if char == ";":
            semicolon_count += 1
            i += 1
            continue

        if char.isalpha() or char == "_":
            start = i
            i += 1
            while i < length and (sql[i].isalnum() or sql[i] in {"_", "$"}):
                i += 1
            tokens.append(sql[start:i].upper())
            continue

        i += 1

    return tokens, semicolon_count


def _skip_line_comment(sql: str, i: int) -> int:
    newline = sql.find("\n", i)
    return len(sql) if newline == -1 else newline + 1


def _skip_block_comment(sql: str, i: int) -> int:
    end = sql.find("*/", i)
    if end == -1:
        raise ReadOnlyViolationError(READ_ONLY_ERROR)
    return end + 2


def _skip_single_quoted(sql: str, i: int) -> int:
    while i < len(sql):
        if sql[i] == "\\":
            i += 2
            continue
        if sql[i] == "'":
            if i + 1 < len(sql) and sql[i + 1] == "'":
                i += 2
                continue
            return i + 1
        i += 1
    raise ReadOnlyViolationError(READ_ONLY_ERROR)


def _skip_double_quoted(sql: str, i: int) -> int:
    while i < len(sql):
        if sql[i] == '"':
            if i + 1 < len(sql) and sql[i + 1] == '"':
                i += 2
                continue
            return i + 1
        i += 1
    raise ReadOnlyViolationError(READ_ONLY_ERROR)


def _skip_backtick_quoted(sql: str, i: int) -> int:
    while i < len(sql):
        if sql[i] == "`":
            if i + 1 < len(sql) and sql[i + 1] == "`":
                i += 2
                continue
            return i + 1
        i += 1
    raise ReadOnlyViolationError(READ_ONLY_ERROR)


def _try_skip_dollar_quoted(sql: str, i: int) -> int | None:
    match = re.match(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$", sql[i:])
    if not match:
        return None
    tag = match.group(0)
    start = i + len(tag)
    end = sql.find(tag, start)
    if end == -1:
        raise ReadOnlyViolationError(READ_ONLY_ERROR)
    return end + len(tag)
