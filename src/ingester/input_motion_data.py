from google.protobuf.json_format import MessageToDict
from naoth.log import Reader as LogReader
from collections import defaultdict
from vaapi.client import Vaapi
from naoth.log import Parser
from pathlib import Path
import logging
import os


def input_representation_done(client, log, representation_list):
    # get the log status - showing how many entries per representation there should be
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log=log.id)
        if len(response) == 0:
            return False
        log_status = response[0]
    except Exception as e:
        print(e)

    # check if number of frames were calculated already
    if not log_status.num_motion_frames or int(log_status.num_motion_frames) == 0:
        print(
            "\tWARNING: first calculate the number of motion frames and put it in the db"
        )
        quit()

    new_list = list()
    for repr in representation_list:
        # if no entry for a given representation is present this will throw an error
        try:
            # query the motion representation and check how many frames with a given representations are there
            model = getattr(client, repr.lower())
            num_repr_frames = model.get_repr_count(log=log.id)["count"]

            if int(getattr(log_status, repr)) != int(num_repr_frames):
                print(
                    f"\t{repr} inserted frames: {num_repr_frames}/{getattr(log_status, repr)}"
                )
                new_list.append(repr)
        except Exception as e:
            print(e)
            new_list.append(repr)

    if len(new_list) > 0:
        print("\tneed to run insertion again")
        print(f"{new_list}")
    return new_list


def input_representation_data(log_root_path, client, log, my_parser, representation_list):
    log_path = Path(log_root_path) / log.sensor_log_path
    # get list of frames  for this log
    frames = client.motionframe.list(log=log.id)
    # Create a dictionary mapping frame_number to id
    frame_to_id = {frame.frame_number: frame.id for frame in frames}

    def get_id_by_frame_number(target_frame_number):
        return frame_to_id.get(target_frame_number, None)

    sensor_log = LogReader(str(log_path), my_parser)
    parsed_messages = defaultdict(list)
    for idx, frame in enumerate(sensor_log):
        # stop parsing log if FrameInfo is missing
        try:
            frame_number = frame["FrameInfo"].frameNumber
        except Exception as e:
            logging.warning(
                f"FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one"
            )
            break
        for repr_name in representation_list:
            try:
                (pos, size) = frame._fields[repr_name]  

                json_obj = {
                    "frame": get_id_by_frame_number(frame_number),
                    "start_pos": pos,
                    "size": size,
                }

                parsed_messages[repr_name].append(json_obj)
            except AttributeError:
                # TODO only print something when in debug mode
                # print("skip frame because representation is not present")
                continue
            except KeyError:
                # if image is not in frame
                continue
            except Exception as e:
                logging.error(
                    f"error parsing {repr} in log {log_path} at frame {idx}"
                )
                logging.error({e})

    chunk_size = 500
    for repr_name, obj_list in parsed_messages.items():
        for i in range(0, len(obj_list), chunk_size):
            # Slice the list from current index 'i' to 'i + chunk_size'
            chunk = obj_list[i : i + chunk_size]
            try:
                print(f"Inserting {len(chunk)} items for {repr_name.lower()} (Index {i})")
                # Dynamically get the model from the client
                model = getattr(client, repr_name.lower())
                
                # Pass ONLY the current slice (chunk) to the API
                model.bulk_create(repr_list=chunk)
                
            except Exception as e:
                print(f"Error inputting data for {log_path}")
                print(f"Failed at {repr_name} index {i}: {e}")
                # Consider 'break' or 'continue' instead of 'quit()' 
                # if you want to try the next representation
                quit()


def get_motion_representations(log):
    motion_repr = log.representation_list["motion_representations"]
    # remove Frameinfo from the list, frameinfo is inserted as frames in db and not a seperate representation
    if "FrameInfo" in motion_repr:
        motion_repr.remove("FrameInfo")

    return motion_repr


def main(log_root_path, client, log):
    log_path = Path(log_root_path) / log.sensor_log_path

    print(f"{log.id}: {log_path}")

    # get
    representation_list = get_motion_representations(log)

    new_representation_list = input_representation_done(client, log, representation_list)
    if len(new_representation_list) == 0:
        print(
            "\tall required representations are already inserted"
        )
        return

    my_parser = Parser()
    input_representation_data(log_root_path, client, log, my_parser, new_representation_list)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.ERROR)

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    def sort_key_fn(log):
        return log.id

    logs = client.logs.list()
    for log in sorted(logs, key=sort_key_fn, reverse=True):
        main("/mnt/repl", client, log)
