from label_studio_sdk import LabelStudio
from utils import check_folder_exists
from utils import check_env_vars
from vaapi.client import Vaapi
import logging
import os

from ingester import (
    input_events,
    input_lab_events,
    input_games,
    input_other_games,
    input_lab_experiments,
    input_videos,
    input_other_video_data,
    input_logs,
    input_experiment_gamelogs,
    process_log_data,
)


def main():
    logging.basicConfig(level=logging.INFO)
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.ERROR)
    check_env_vars()
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    if not check_folder_exists(log_root_path):
        logging.getLogger().error(f"Log Path at {log_root_path} is not accessible")

    # TODO maybe build a class LogCrawler and all the functions are member functions and the clients and prometheus config objects are also members
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    l_client = LabelStudio(
        base_url="https://labelstudio-api.berlin-united.com",
        api_key=os.environ.get("LABELSTUDIO_API_KEY"),
    )
    # 01
    input_events(log_root_path, v_client)
    input_lab_events(log_root_path, v_client)
    # 02
    input_games(log_root_path, v_client)
    input_other_games(log_root_path, v_client)
    # 03
    input_lab_experiments(log_root_path, v_client)
    # 04
    input_videos(log_root_path, v_client)
    input_other_video_data(log_root_path, v_client)
    # 05
    input_logs(log_root_path, v_client)
    input_experiment_gamelogs(log_root_path, v_client)

    # 06 handle log data
    process_log_data(log_root_path, v_client, l_client)
    logging.info("########################################")
    logging.info("################# Done #################")
    logging.info("########################################")


if __name__ == "__main__":
    main()
