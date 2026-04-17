from pathlib import Path
import logging
import os


def check_env_vars():
    if "VAT_LOG_ROOT" not in os.environ:
        logging.getLogger().error("Error VAT_LOG_ROOT variable not found")

    if "VAT_API_URL" not in os.environ:
        logging.getLogger().error("Error VAT_API_URL variable not found")

    if "VAT_API_TOKEN" not in os.environ:
        logging.getLogger().error("Error VAT_API_TOKEN variable not found")


def check_folder_exists(path):
    if Path(path).exists():
        return True
    else:
        return False
