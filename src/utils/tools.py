from prometheus_client import Counter, CollectorRegistry
from pathlib import Path
import logging
import os

registry = CollectorRegistry()
ERROR_COUNT = Counter("logcrawler_errors", "logcrawler_errors", registry=registry)


def check_env_vars():
    if "VAT_LOG_ROOT" not in os.environ:
        logging.getLogger().error("Error VAT_LOG_ROOT variable not found")
        ERROR_COUNT.inc()
    if "VAT_API_URL" not in os.environ:
        logging.getLogger().error("Error VAT_API_URL variable not found")
        ERROR_COUNT.inc()
    if "VAT_API_TOKEN" not in os.environ:
        logging.getLogger().error("Error VAT_API_TOKEN variable not found")

        ERROR_COUNT.inc()


def check_folder_exists(path):
    if Path(path).exists():
        return True
    else:
        return False
