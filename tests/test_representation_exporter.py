"""
Representation Exporter
"""
from naoth.log import Reader as LogReader
from naoth.log import Parser
from pathlib import Path
import logging
import os
import json


def is_done(log, representation_file: str, force_flag: bool) -> bool:
    if force_flag:
        logging.info("\tforce flag is set - will parse log")
        return False

    repr_list_missing = True
    # Check if the file contains the keys we expect
    # TODO dont return yet we still need to check the data base
    if representation_file.is_file():
        with open(str(representation_file), "r") as f:
            representations = json.load(f)
            # check if we have the keys we expect in the file
            if (
                "cognition_representations" not in representations
                or "motion_representations" not in representations
            ):
                logging.info(
                    "\tcognition_representations motion_representations field is missing in json file - will parse log"
                )
                repr_list_missing = False
    else:
        return False

    # check if data is in in the log model
    db_repr_dict = log.representation_list
    if (
        "cognition_representations" not in db_repr_dict
        or "motion_representations" not in db_repr_dict
    ):
        logging.info(
            "\tcognition_representations motion_representations field is missing in db - will parse log"
        )
        repr_list_missing = False

    return repr_list_missing





log_path = Path("/mnt/d/repl/2025-07-15_RC25/2025-07-17_11-45-00_Berlin United_vs_Nao Devils_half1/game_logs/1_15_Nao0006_250717-1504")
