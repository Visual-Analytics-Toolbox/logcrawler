from typing import Generator, List
from pathlib import Path
from time import sleep
import logging
import os


logger = logging.getLogger(__name__)


def scandir_yield_files(directory):
    """Generator that yields file paths in a directory."""
    with os.scandir(directory) as it:
        for entry in it:
            if entry.is_file():
                yield entry.path


def path_generator(
    directory: str, 
    batch_size: int = 200
) -> Generator[List[str], None, None]:
    batch = []
    for path in scandir_yield_files(directory):
        batch.append(path)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def handle_insertion(client, log_root_path, individual_extracted_folder, log, camera, image_type):
    logger.debug(f"\tadding images from {individual_extracted_folder} to db")

    # return silently if the folder does not exist or the argument is not a folder
    # this could be the case for the raw image folder if now raw images exist in the logs and therefore were not extracted
    if not Path(individual_extracted_folder).is_dir():
        return

    if is_done(client, log.id, camera, image_type):
        return

    # get list of frames  for this log
    frames = client.cognitionframe.list(log=log.id)
    # Create a dictionary mapping frame_number to id
    frame_to_id = {frame.frame_number: frame.id for frame in frames}

    def get_id_by_frame_number(target_frame_number):
        return frame_to_id.get(target_frame_number, None)

    for batch in path_generator(individual_extracted_folder):
        image_ar = [None] * len(batch)
        for idx, file in enumerate(batch):
            # get frame number
            framenumber = int(Path(file).stem)
            frame_id = get_id_by_frame_number(framenumber)
            if not frame_id:
                print("ERROR: frame id not in db")
                print(f"frame num:  {framenumber} - log id: {log.id}")
                print(f"{log.log_path}")
                print(
                    "You should run the image extraction again with force flag for this log"
                )
                quit()

            url_path = str(file).removeprefix(log_root_path).strip("/")

            image_ar[idx] = {
                "frame": frame_id,
                "camera": camera,
                "type": image_type,
                "image_url": url_path,
                # HACK we need to provide some default values
                "blurredness_value": None,
                "brightness_value": None,
                "resolution": None,
            }
        try:
            _ = client.image.bulk_create(data_list=image_ar)
        except Exception as e:
            print(f"error inputing the data {log.log_path}")
            print(e)
            return

        sleep(0.5)
    # sleep(5)


def is_done(client, log_id, camera, image_type):
    response = client.image.get_image_count(log=log_id, camera=camera, type=image_type)
    db_count = int(response["count"])

    response2 = client.log_status.list(log=log_id)
    if len(response2) == 0:
        logger.error("\tno log_status found")
        return False
    log_status = response2[0]

    if camera == "BOTTOM" and image_type == "RAW":
        target_count = int(log_status.Image)
    elif camera == "TOP" and image_type == "RAW":
        target_count = int(log_status.ImageTop)
    elif camera == "BOTTOM" and image_type == "JPEG":
        target_count = int(log_status.ImageJPEG)
    elif camera == "TOP" and image_type == "JPEG":
        target_count = int(log_status.ImageJPEGTop)
    else:
        raise ValueError()

    if target_count == db_count:
        logger.debug("\t\tall images are already inserted")
        return True
    logger.warning(f"\t\tmissing {target_count} images in the db")
    return False


def input_images(log_root_path, client, log):
    logging.info("\t\tInput Images")

    log_path = Path(log_root_path) / log.log_path

    # TODO could we just switch game_logs with extracted in the paths?
    # FIXME handle experiments here
    robot_foldername = log_path.parent.name
    
    if not log.game:
        extracted_path = log_path.parent / "extracted"
    else:
        extracted_path = log_path.parent.parent.parent / "extracted" / robot_foldername
    
    bottom_path = extracted_path / "log_bottom"
    top_path = extracted_path / "log_top"
    bottom_path_jpg = extracted_path / "log_bottom_jpg"
    top_path_jpg = extracted_path / "log_top_jpg"

    handle_insertion(client, log_root_path, bottom_path, log, camera="BOTTOM", image_type="RAW")
    handle_insertion(client, log_root_path, top_path, log, camera="TOP", image_type="RAW")
    handle_insertion(client, log_root_path, bottom_path_jpg, log, camera="BOTTOM", image_type="JPEG")
    handle_insertion(client, log_root_path, top_path_jpg, log, camera="TOP", image_type="JPEG")
