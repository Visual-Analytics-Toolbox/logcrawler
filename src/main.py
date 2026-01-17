from vaapi.client import Vaapi
from prometheus_client import push_to_gateway
from utils import check_env_vars, registry
from ingester import (
    input_events,
    input_lab_events,
    input_lab_experiments,
    input_games,
    input_videos,
    input_logs,
    combine_logs,
    export_representation,
)
from utils import check_folder_exists
import logging
import os


def main():
    logging.basicConfig(level=logging.INFO)
    check_env_vars()
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    if not check_folder_exists(log_root_path):
        logging.getLogger().error(f"Log Path at {log_root_path} is not accessible")

    # TODO maybe build a class LogCrawler and all the functions are member functions and the clients and prometheus config objects are also members
    # TODO catch errors here
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    input_events(log_root_path, client)
    input_lab_events(log_root_path, client)
    input_games(log_root_path, client)
    input_lab_experiments(log_root_path, client)
    input_videos(log_root_path, client)
    input_logs(log_root_path, client)
    combine_logs(log_root_path, client)
    export_representation(log_root_path, client)
    # create representation json
    # add robot pose + patch representation file (maybe logstatus?)

    logging.info("########################################")
    logging.info("################# Done #################")
    logging.info("########################################")
    push_to_gateway(
        "http://monitoring-prometheus-pushgateway.monitoring.svc.cluster.local:9091",
        job="logcrawler",
        registry=registry,
    )


if __name__ == "__main__":
    main()
