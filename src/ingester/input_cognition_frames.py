from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.log import Parser
from google.protobuf.json_format import MessageToDict
import logging

def input_frames_done(client, log_id):
    # get the log status object for this log
    try:
        # we use list here because we only know the log_id here and not the id of the logstatus object
        response = client.log_status.list(log=log_id)
        if len(response) == 0:
            return False
        log_status = response[0]
    except Exception as e:
        print(e)

    # abort if Logstatus reports no Cognition frames for this log
    if not log_status.FrameInfo or int(log_status.FrameInfo) == 0:
        print(
            "\tWARNING: first calculate the number of cognition frames and put it in the db"
        )
        quit()

    response = client.cognitionframe.get_frame_count(log=log_id)
    if int(log_status.FrameInfo) == int(response["count"]):
        return True
    elif int(response["count"]) > int(log_status.FrameInfo):
        # rust based calculation for num frames stops if one broken representation is in the last frame
        print("ERROR: there are more frames in the database than they should be")
        print(
            f"Run logstatus calculation again for log {log_id} or make sure the end of the log is calculated the same way"
        )
        quit()
    else:
        print(
            f"\t number of frames is not correct: {log_status.FrameInfo} != {response['count']}"
        )
        return False

def input_cognition_frames(log_root_path, client):
    logging.info("################# Input Cognition Frame Data #################")
    existing_data = client.logs.list()

    def sort_key_fn(log):
        return log.id
    
    for log in sorted(existing_data, key=sort_key_fn):
        log_path = Path(log_root_path) / log.log_path

        print(f"{log.id}: {log_path}")

        if  input_frames_done(client, log.id):
            print("All Cognition Frames are already in the db")
            continue

        my_parser = Parser()
        game_log = LogReader(str(log_path), my_parser)
        parsed_messages = list()
        for idx, frame in enumerate(game_log):
            # stop parsing log if FrameInfo is missing
            try:
                frame_number = frame["FrameInfo"].frameNumber
            except Exception as e:
                logging.warning(
                    "FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one"
                )
                break
            
            json_obj = {
                "log": log.id,
                "frame_number": frame["FrameInfo"].frameNumber,
                "frame_time": frame["FrameInfo"].time,
            }
            parsed_messages.append(json_obj)
            if idx % 1000 == 0:
                try:
                    _ = client.cognitionframe.bulk_create(frame_list=parsed_messages)
                    parsed_messages.clear()
                except Exception as e:
                    print(f"error inputing the data for {log_path}")
                    print(e)
                    quit()
        try:
            _ = client.cognitionframe.bulk_create(frame_list=parsed_messages)
        except Exception as e:
            print(e)
            print(f"error inputing the data {log_path}")