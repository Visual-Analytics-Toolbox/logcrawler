from naoth.log import Reader as LogReader
from vaapi.client import Vaapi
from naoth.log import Parser
from pathlib import Path
import logging
import os


logger = logging.getLogger(__name__)


def input_frames_done(client, log_id):
    # get the log status object for this log
    try:
        # we use list here because we only know the log_id here and not the id of the logstatus object
        response = client.log_status.list(log=log_id)
        if len(response) == 0:
            return False
        log_status = response[0]
    except Exception as e:
        logger.error(e)

    # abort if Logstatus reports no Motion frames for this log
    if not log_status.num_motion_frames or int(log_status.num_motion_frames) == 0:
        logger.error(
            "\tfirst calculate the number of motion frames and put it in the db"
        )
        quit()

    response = client.motionframe.get_frame_count(log=log_id)
    if int(log_status.num_motion_frames) == int(response["count"]):
        return True
    elif int(response["count"]) > int(log_status.num_motion_frames):
        # rust based calculation for num frames stops if one broken representation is in the last frame
        logger.error("ERROR: there are more frames in the database than they should be")
        logger.error(
            f"Run logstatus calculation again for log {log_id} or make sure the end of the log is calculated the same way"
        )
        quit()
    else:
        logger.error(
            f"\t number of frames is not correct: {log_status.num_motion_frames} != {response['count']}"
        )
        return False


def input_motion_frames(log_root_path, client, log):
    logging.info("\t\tInput Motion Frames")

    log_path = Path(log_root_path) / log.sensor_log_path
    if  input_frames_done(client, log.id):
        logger.debug("All Motion Frames are already in the db")
        return

    my_parser = Parser()
    game_log = LogReader(str(log_path), my_parser)
    parsed_messages = list()
    for idx, frame in enumerate(game_log):
        # stop parsing log if FrameInfo is missing
        try:
            frame_number = frame["FrameInfo"].frameNumber
        except Exception as e:
            logger.warning(
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
                _ = client.motionframe.bulk_create(frame_list=parsed_messages)
                parsed_messages.clear()
            except Exception as e:
                print(f"error inputing the data for {log_path}")
                print(e)
                quit()
    try:
        _ = client.motionframe.bulk_create(frame_list=parsed_messages)
    except Exception as e:
        print(e)
        print(f"error inputing the data {log_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.ERROR)

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    input_motion_frames("/mnt/repl", client)
