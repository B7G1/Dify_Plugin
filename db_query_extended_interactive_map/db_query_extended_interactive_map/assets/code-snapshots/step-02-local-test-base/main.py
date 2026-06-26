"""Dify Plugin entry point for the database query scaffold."""

import logging

from dify_plugin import DifyPluginEnv, Plugin


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))


if __name__ == "__main__":
    logger.info("Starting db_query_extended plugin scaffold")
    plugin.run()
