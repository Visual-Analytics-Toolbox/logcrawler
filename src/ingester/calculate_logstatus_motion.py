from pathlib import Path
import logging
from naoth.log import Reader as LogReader
from naoth.log import Parser
from google.protobuf.json_format import MessageToDict


def is_done_motion(log_id, status_dict, client):
    new_dict = status_dict.copy()
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log=log_id)
        if len(response) == 0:
            return status_dict
        log_status = response[0]

        for k, v in status_dict.items():
            if k == "FrameInfo":
                field_value = getattr(log_status, "num_motion_frames")
            else:
                field_value = getattr(log_status, k)

            if field_value is None:
                logging.warning(f"\tdid not find a value for repr {k}")
            else:
                new_dict.pop(k)
        return new_dict
    # TODO would be nice to handle the vaapi API error here explicitely
    except Exception as e:
        logging.error("error", e)
        quit()
        return status_dict


def add_sensorlog_representations(log, sensor_log_path, client, force):
    # get list of representations from db
    motion_repr_names = log.representation_list["motion_representations"]
    # make a dictionary out of the representation names which can later be used to count
    motion_status_dict = dict.fromkeys(motion_repr_names, 0)

    new_motion_status_dict = is_done_motion(log.id, motion_status_dict, client)
    if not force and len(new_motion_status_dict) == 0:
        print("\twe already calculated number of full sensor frames for this log")
    else:
        if force:
            new_motion_status_dict = motion_status_dict

        my_parser = Parser()
        game_log = LogReader(str(sensor_log_path), my_parser)
        for idx, frame in enumerate(game_log):
            # stop parsing log if FrameInfo is missing
            try:
                frame_number = frame['FrameInfo'].frameNumber
            except Exception as e:
                logging.warning(f"FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one")
                break
            for repr in new_motion_status_dict:
                try:
                    data = MessageToDict(frame[repr])
                    new_motion_status_dict[repr] += 1
                except AttributeError:
                    # TODO only print something when in debug mode
                    #print("skip frame because representation is not present")
                    continue
                except Exception as e:
                    logging.error(f"error parsing {repr} in log {sensor_log_path} at frame {idx}")
                    logging.error({e})

        try:
            if "FrameInfo" in new_motion_status_dict:
                new_motion_status_dict["num_motion_frames"] = (
                    new_motion_status_dict.pop("FrameInfo")
                )

            logging.debug(new_motion_status_dict)
            _ = client.log_status.update(log=log.id, **new_motion_status_dict)
        except Exception as e:
            logging.error(f"\terror inputing the data {sensor_log_path}")
            logging.error(e)
            quit()


def calculate_logstatus_motion(log_root_path, client):
    existing_data = client.logs.list()

    def sort_key_fn(log):
        return log.id

    for log in sorted(existing_data, key=sort_key_fn):
        sensor_log_path = Path(log_root_path) / log.sensor_log_path

        logging.info(f"{log.id}: {sensor_log_path}")
        add_sensorlog_representations(log, sensor_log_path, client, force=False)
