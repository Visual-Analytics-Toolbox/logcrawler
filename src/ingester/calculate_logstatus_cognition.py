from pathlib import Path
import logging
from naoth.log import Reader as LogReader
from naoth.log import Parser
from google.protobuf.json_format import MessageToDict


def is_done(log_id, status_dict, client):
    new_dict = status_dict.copy()
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log=log_id)
        if len(response) == 0:
            return status_dict
        log_status = response[0]

        invalid_data = False
        for k, v in status_dict.items():
            field_value = getattr(log_status, k)
            # print(k, v, field_value)
            if field_value is None:
                logging.warning(f"\tdid not find a value for repr {k}")
            elif field_value > log_status.FrameInfo:
                invalid_data = True
                logging.warning(f"\tfound value exceeding number of full frames for repr {k}")
            else:
                new_dict.pop(k)
        # Include FrameInfo when we have representations that exceed the number of FrameInfos
        # Covers the case that the number of FrameInfos was calculated wrongly
        if invalid_data:
            new_dict.update({"FrameInfo": 0})

        return new_dict
    # TODO would be nice to handle the vaapi API error here explicitely
    except Exception as e:
        logging.error("error", e)
        quit()
        return status_dict


def add_gamelog_representations(log, log_path, client, force):
    # get list of representations from db
    cognition_repr_names = log.representation_list["cognition_representations"]
    if "RoleDecisionModel" in cognition_repr_names: cognition_repr_names.remove("RoleDecisionModel")
    # make a dictionary out of the representation names which can later be used to count
    cognition_status_dict = dict.fromkeys(cognition_repr_names, 0)

    new_cognition_status_dict = is_done(log.id, cognition_status_dict, client)
    if not force and len(new_cognition_status_dict) == 0:
         logging.warning("\twe already calculated number of full cognition frames for this log")
    else:
        if force:
            new_cognition_status_dict = cognition_status_dict

        my_parser = Parser()
        my_parser.register("FieldPerceptTop", "FieldPercept")
        my_parser.register("GoalPerceptTop", "GoalPercept")
        my_parser.register("FieldPerceptTop", "FieldPercept")
        my_parser.register("BallCandidatesTop", "BallCandidates")
        my_parser.register("ImageTop", "Image")
        my_parser.register("ImageJPEG"   , "Image")
        my_parser.register("ImageJPEGTop", "Image")

        game_log = LogReader(str(log_path), my_parser)
        for idx, frame in enumerate(game_log):
            # stop parsing log if FrameInfo is missing
            try:
                frame_number = frame['FrameInfo'].frameNumber
            except Exception as e:
                logging.warning(f"FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one")
                break
            # TODO: speed it up by removing representations that we dont care about in this dict
            for repr in new_cognition_status_dict:
                try:
                    data = MessageToDict(frame[repr])
                    new_cognition_status_dict[repr] += 1
                except AttributeError:
                    # TODO only print something when in debug mode
                    #print("skip frame because representation is not present")
                    continue
                except KeyError:
                    # if image is not in frame
                    continue
                except Exception as e:
                    logging.error(f"error parsing {repr} in log {log_path} at frame {idx}")
                    logging.error({e})

        logging.debug(new_cognition_status_dict)
        try:
            _ = client.log_status.update(log=log.id, **new_cognition_status_dict)
        except Exception as e:
            logging.error(e)
            logging.error(f"\terror inputing the data {log_path}")
            quit()


def calculate_logstatus_cognition(log_root_path, client):
    existing_data = client.logs.list()

    def sort_key_fn(log):
        return log.id

    for log in sorted(existing_data, key=sort_key_fn):
        # TODO use combined log if its a file. -> it should always be a file if not experiment
        # FIXME handle the case that combined log is not a file here directly
        combined_log_path = Path(log_root_path) / log.combined_log_path

        logging.info(f"{log.id}: {combined_log_path}")
        add_gamelog_representations(log, combined_log_path, client, force=False)



