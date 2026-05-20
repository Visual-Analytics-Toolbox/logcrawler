from vaapi.client import Vaapi
from pathlib import Path
import subprocess
import logging
import json
import os


logger = logging.getLogger(__name__)


def create_frame_mappings(frames, frame_count, images_generator, concat_file_path, json_filename, log_root_path):
    image_lookup = {img.frame.id: img.image_url for img in images_generator}

    last_valid_url = None
    pending_duration = 0.0
    last_valid_frame_number = None
    mapping_data = []
    current_pts = 0.0  # Video time starts at 0.0 seconds

    with open(str(concat_file_path), "w") as concat_file:
        for idx, frame in enumerate(frames):
            
            # skip first frames if the gaps are too large
            if idx < 2:
                if frames[idx+1].frame_number - frame.frame_number > 30:
                    print(f"skipping frame {frame.frame_number}")
                    continue

            # 1. Calculate duration for the current frame slot
            if idx < frame_count - 1:
                duration = (frames[idx+1].frame_time - frame.frame_time) / 1000
            else:
                duration = 0.033  # Placeholder for the final frame

            image_url = image_lookup.get(frame.id)

            if image_url:
                # If we already have a previous image waiting to be written, write it now
                # with all the accumulated duration from any missing frames that followed it
                if last_valid_url is not None:
                    concat_file.write(f"file '{log_root_path}/{last_valid_url}'\n")
                    concat_file.write(f"duration {pending_duration}\n")

                    mapping_data.append({
                        "pts": round(current_pts, 4),
                        "duration": round(pending_duration, 4),
                        "robot_frame": last_valid_frame_number
                    })
                    # Advance the video timeline by the duration we just committed
                    current_pts += pending_duration
                
                # Reset the tracker for this new valid image
                last_valid_url = image_url
                last_valid_frame_number = frame.frame_number
                pending_duration = duration
            else:
                # No image for this frame! 
                # Accumulate this duration into the last known valid image
                pending_duration += duration

        # After the loop finishes, we must write out the very last valid image 
        # with whatever remaining duration it accumulated
        if last_valid_url is not None:
            concat_file.write(f"file '{log_root_path}/{last_valid_url}'\n")
            concat_file.write(f"duration {pending_duration}\n")
            
            mapping_data.append({
                "pts": round(current_pts, 4),
                "duration": round(pending_duration, 4),
                "robot_frame": last_valid_frame_number
            })
            # FFmpeg concat format requires repeating the final file entry without a duration
            concat_file.write(f"file '{log_root_path}/{last_valid_url}'\n")

    with open(str(json_filename), "w") as json_file:
        json.dump(mapping_data, json_file, indent=2)


def create_frame_videos(log_root_path, client, log):
    log_path = Path(log_root_path) / Path(log.combined_log_path)

    if not log.game:
        extracted_folder = str(log_path.parent / "extracted")
    else:
        extracted_folder = str(log_path.parent).replace("game_logs", "extracted")

    bottom_folder = Path(extracted_folder) / "log_bottom_jpg"
    top_folder = Path(extracted_folder) / "log_top_jpg"
    
    # abort if no jpeg logs
    if not bottom_folder.exists():
        return
    if not top_folder.exists():
        return
    
    bottom_concat_file_path = Path(extracted_folder) / "bottom.txt"
    bottom_json_filename = Path(extracted_folder) / "bottom.json"
    bottom_video_filename = Path(extracted_folder) / "bottom.mp4"
    top_concat_file_path = Path(extracted_folder) / "top.txt"
    top_json_filename = Path(extracted_folder) / "top.json"
    top_video_filename = Path(extracted_folder) / "top.mp4"

    if bottom_video_filename.exists() and bottom_json_filename.exists():
        return
    if top_video_filename.exists() and top_json_filename.exists():
        return

    # get the number of frames and number of images per camera - abort if the ratio is off
    frame_count = client.cognitionframe.get_frame_count(log=log.id)["count"]
    bottom_image_count = client.image.get_image_count(log=log.id, camera="BOTTOM")["count"]
    top_image_count = client.image.get_image_count(log=log.id, camera="TOP")["count"]
    print(log.id, frame_count, bottom_image_count, top_image_count, top_image_count/frame_count)

    if top_image_count/frame_count < 0.97:
        return    
    if bottom_image_count/frame_count < 0.97:
        return
    
    def sort_key_fn(frame):
        return frame.frame_time

    frame_iterator = client.cognitionframe.list(log=log.id)
    frames = list(frame_iterator)
    frames = sorted(frames, key=sort_key_fn)
    
    all_top_images_generator = client.image.list(log=log.id, camera="TOP", limit=300)
    all_bottom_images_generator = client.image.list(log=log.id, camera="TOP", limit=300)

    create_frame_mappings(frames, frame_count, all_top_images_generator, top_concat_file_path, top_json_filename, log_root_path)
    create_frame_mappings(frames, frame_count, all_bottom_images_generator, bottom_concat_file_path, bottom_json_filename, log_root_path)

    create_video_file(top_concat_file_path, top_video_filename)
    create_video_file(bottom_concat_file_path, bottom_video_filename)


def create_video_file(concat_file_path, video_filename):
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(video_filename)
    ]
    
    print("Running FFmpeg to generate video...")
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f" Success! Video created: {video_filename}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during FFmpeg execution: {e}")


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
    for log in sorted(logs, key=sort_key_fn, reverse=False):
        create_frame_videos("/mnt/repl", client, log)
        