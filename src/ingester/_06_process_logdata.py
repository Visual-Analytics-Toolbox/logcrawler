"""
    This script runs all the log specific functions. The newest log in the db is processed first and all information from this log is inserted in the database
"""
from .calculate_logstatus_cognition import (calculate_logstatus_cognition as calculate_logstatus_cognition)
from .calculate_logstatus_motion import (calculate_logstatus_motion as calculate_logstatus_motion)
from .calculate_closest_frame import calculate_closest_frames as calculate_closest_frames
from .input_cognition_frames import input_cognition_frames as input_cognition_frames
from .representation_exporter import export_representation as export_representation
from .calculate_image_stats import calculate_image_stats as calculate_image_stats
from .sync_labelstudio import run_labelstudio_insert as run_labelstudio_insert
from .input_motion_frames import input_motion_frames as input_motion_frames
from .input_cognition_data import main as input_cognition_data_main
from .extract_images import extract_images as extract_images
from .combine_logs import combine_logs as combine_logs
from .input_images import input_images as input_images
import logging


def sort_key_fn(data):
    return data.log_path


def process_log_data(log_root_path, v_client, l_client):
    logs = v_client.logs.list()
    # TODO load logs in memory
    for log in sorted(logs, key=sort_key_fn, reverse=True):
        logging.info(f"######## Process Log {log} ########")
        combine_logs(log_root_path, v_client, log, force=False)
        export_representation(log_root_path, v_client, log, force=False)
        calculate_logstatus_cognition(log_root_path, v_client, log)
        calculate_logstatus_motion(log_root_path, v_client, log, force=False)
        input_cognition_frames(log_root_path, v_client, log)
        input_motion_frames(log_root_path, v_client, log)
        calculate_closest_frames(v_client, log)
        extract_images(log_root_path, v_client, log)
        input_images(log_root_path, v_client, log)
        run_labelstudio_insert(v_client, l_client, log)
        calculate_image_stats(log_root_path, v_client, log)
        input_cognition_data_main(log_root_path, v_client, log)
