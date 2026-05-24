from naoth.log import Reader as LogReader
from PIL import Image as PIL_Image
from vaapi.client import Vaapi
from naoth.log import Parser
from pathlib import Path
import numpy as np
import subprocess
import logging
import json
import os
import io


logger = logging.getLogger(__name__)


def image_from_proto_jpeg(message):
    # hack:
    if message.format == message.JPEG:
        # unpack JPG
        img = PIL_Image.open(io.BytesIO(message.data))

        # HACK: for some reason the decoded image is inverted ...
        yuv422 = 255 - np.array(img, dtype=np.uint8)

        # flatten the image to get the same data formal like a usual yuv422
        yuv422 = yuv422.reshape(message.height * message.width * 2)
    else:
        # read each channel of yuv422 separately
        yuv422 = np.frombuffer(message.data, dtype=np.uint8)

    y = yuv422[0::2]
    u = yuv422[1::4]
    v = yuv422[3::4]

    # convert from yuv422 to yuv888
    yuv888 = np.zeros(message.height * message.width * 3, dtype=np.uint8)

    yuv888[0::3] = y
    yuv888[1::6] = u
    yuv888[2::6] = v
    yuv888[4::6] = u
    yuv888[5::6] = v

    yuv888 = yuv888.reshape((message.height, message.width, 3))

    # convert the image to rgb
    img = PIL_Image.frombytes(
        "YCbCr", (message.width, message.height), yuv888.tobytes()
    )
    rgb_frame = img.convert("RGB")
    frame_bytes = rgb_frame.tobytes()

    return frame_bytes


def create_top_video(log_root_path, client, log):
    if log.top_video_path  is not None:
        a = Path(log_root_path) / Path(log.top_video_path)
        if a.exists():
            return

    log_path = Path(log_root_path) / Path(log.combined_log_path)
    if not log.game:
        extracted_folder = str(log_path.parent / "extracted")
    else:
        extracted_folder = str(log_path.parent).replace("game_logs", "extracted")

    top_folder = Path(extracted_folder) / "log_top_jpg"
    
    # abort if no jpeg logs
    if not top_folder.exists():
        return
    
    frame_count = client.cognitionframe.get_frame_count(log=log.id)["count"]
    top_image_count = client.image.get_image_count(log=log.id, camera="TOP")["count"]

    if top_image_count/frame_count < 0.97:
        return  

    top_json_filename = Path(extracted_folder) / "top.json"
    top_video_filename = Path(extracted_folder) / "top.mp4"

    my_parser = Parser()
    my_parser.register("ImageJPEGTop", "Image")

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",          # Input format is raw uncompressed video frames
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",       # PIL standard RGB format
        "-s", f"{640}x{480}", # FFmpeg NEEDS the resolution for raw video
        "-r", "30",                # Framerate
        "-i", "-",                 # Read from stdin
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",     # Output format (standard for MP4 playback)
        str(top_video_filename)
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    last_valid_frame = None
    mapping_data = []
    current_pts = 0.0
    duration =  0.033
    with LogReader(log_path, my_parser) as reader:
        for frame in reader.read():
            try:
                frame_number = frame["FrameInfo"].frameNumber
                frame_time = frame["FrameInfo"].time
            except Exception as e:
                print(e)
                print(
                    "FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one"
                )
                break
            try:
                image_top_jpeg = image_from_proto_jpeg(frame["ImageJPEGTop"])
                last_valid_frame = image_top_jpeg
            except KeyError:
                image_top_jpeg = last_valid_frame

            if image_top_jpeg is not None:
                process.stdin.write(image_top_jpeg)

                mapping_data.append({
                    "pts": round(current_pts, 4),
                    "duration": round(duration, 4),
                    "frame_number": frame_number
                })
    process.stdin.close()
    process.wait()

    with open(str(str(top_json_filename)), "w") as json_file:
        json.dump(mapping_data, json_file, indent=2)
    
    # patch log object
    client.logs.update(
        id=log.id,
        top_video_path=top_video_filename,
    )


def create_bottom_video(log_root_path, client, log):
    if log.bottom_video_path is not None:
        a = Path(log_root_path) / Path(log.bottom_video_path)
        if a.exists():
            return

    log_path = Path(log_root_path) / Path(log.combined_log_path)
    if not log.game:
        extracted_folder = str(log_path.parent / "extracted")
    else:
        extracted_folder = str(log_path.parent).replace("game_logs", "extracted")

    bottom_folder = Path(extracted_folder) / "log_bottom_jpg"
    
    # abort if no jpeg logs
    if not bottom_folder.exists():
        return
    
    frame_count = client.cognitionframe.get_frame_count(log=log.id)["count"]
    bottom_image_count = client.image.get_image_count(log=log.id, camera="BOTTOM")["count"]

    if bottom_image_count/frame_count < 0.97:
        return  

    bottom_json_filename = Path(extracted_folder) / "bottom.json"
    bottom_video_filename = Path(extracted_folder) / "bottom.mp4"

    my_parser = Parser()
    my_parser.register("ImageJPEG", "Image")
    my_parser.register("ImageJPEGTop", "Image")

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",          # Input format is raw uncompressed video frames
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",       # PIL standard RGB format
        "-s", f"{640}x{480}", # FFmpeg NEEDS the resolution for raw video
        "-r", "30",                # Framerate
        "-i", "-",                 # Read from stdin
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",     # Output format (standard for MP4 playback)
        str(bottom_video_filename)
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    last_valid_frame = None
    mapping_data = []
    current_pts = 0.0
    duration =  0.033

    with LogReader(log_path, my_parser) as reader:
        for frame in reader.read():
            try:
                frame_number = frame["FrameInfo"].frameNumber
                frame_time = frame["FrameInfo"].time
            except Exception as e:
                print(e)
                print(
                    "FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one"
                )
                break

            try:
                image_bottom_jpeg = image_from_proto_jpeg(frame["ImageJPEG"])
                last_valid_frame = image_bottom_jpeg
            except KeyError:
                image_bottom_jpeg = last_valid_frame

            if image_bottom_jpeg is not None:
                process.stdin.write(image_bottom_jpeg)

                mapping_data.append({
                    "pts": round(current_pts, 4),
                    "duration": round(duration, 4),
                    "frame_number": frame_number
                })

    process.stdin.close()
    process.wait()
    with open(str(bottom_json_filename), "w") as json_file:
        json.dump(mapping_data, json_file, indent=2)

    # patch log object
    client.logs.update(
        id=log.id,
        bottom_video_path=bottom_video_filename,
    )
    

def create_frame_videos(log_root_path, client, log):
    logging.info("\t\tCreate Videos for log")
    
    create_top_video(log_root_path, client, log)
    create_bottom_video(log_root_path, client, log)


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
        if log.id < 1000:
            continue
        print(log.id, log.log_path)
        create_frame_videos("/mnt/repl", client, log)
        quit()