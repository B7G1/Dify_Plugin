"""Dify Plugin entry point for the database query scaffold."""

import logging

from dify_plugin import DifyPluginEnv, Plugin


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))


def main() -> None:
    """Start the SDK-managed plugin runtime and preserve startup failures."""
    logger.info("Starting db_query_extended plugin; tool registration is declared in manifest.yaml")
    try:
        plugin.run()
    except Exception:
        logger.exception("db_query_extended plugin failed during startup")
        raise


if __name__ == "__main__":
    main()
