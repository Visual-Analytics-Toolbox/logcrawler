from pathlib import Path
import logging


event_list = ["2024-07-15_RC24", "2025-03-12-GO25", "2025-07-15_RC25"]
lab_experiments = ["2026_lab-tests"]
# TODO: at ifa and other test events we play against ourselves: how should we deal with this in our db?


def input_events(log_root_path, client):
    logging.info("################# Input Event Data #################")
    all_events = [f for f in Path(log_root_path).iterdir() if f.is_dir()]
    for event in sorted(all_events):
        if event.name in event_list:
            logging.debug(f"handle {event.name} event")
            event_list.remove(event.name)
            if Path(event / "comments.txt").is_file():
                with open(event / "comments.txt") as f:
                    comment = f.read()
            else:
                # logging.getLogger().info(
                #    f"No comments.txt found for event {event.name}"
                # )
                comment = ""
            try:
                new_event = client.events.create(
                    name=event.name,
                    event_folder=str(event).removeprefix(log_root_path).strip("/"),
                    comment=comment,
                )
                logging.debug(f"inserted event: {new_event}")
            except Exception as e:
                logging.error(
                    f"following error occured when trying to insert event {event.name}:{e}"
                )

    # check if event folder that are specified in the list where found
    if len(event_list) > 0:
        for event in event_list:
            logging.warning(f"Couldn't find the {event} event folder")


def input_lab_events(log_root_path, client):
    logging.info("################# Input Lab Experiments #################")
    all_events = [f for f in Path(log_root_path).iterdir() if f.is_dir()]
    for event in sorted(all_events):
        if event.name in lab_experiments:
            logging.debug(f"handle {event.name} event")
            lab_experiments.remove(event.name)
            if Path(event / "comments.txt").is_file():
                with open(event / "comments.txt") as f:
                    comment = f.read()
            else:
                # logging.getLogger().info(
                #    f"No comments.txt found for event {event.name}"
                # )
                comment = ""
            try:
                new_event = client.events.create(
                    name=event.name,
                    event_folder=str(event).removeprefix(log_root_path).strip("/"),
                    comment=comment,
                )
                logging.debug(f"inserted event: {new_event}")
            except Exception as e:
                logging.error(
                    f"following error occured when trying to insert event {event.name}:{e}"
                )

    # check if event folder that are specified in the list where found
    if len(lab_experiments) > 0:
        for event in lab_experiments:
            logging.warning(f"Couldn't find the {event} event folder")
