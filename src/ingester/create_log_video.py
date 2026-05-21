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
    skipped_frames = 0
    mapping_data = []
    current_pts = 0.0  # Video time starts at 0.0 seconds

    with open(str(concat_file_path), "w") as concat_file:
        for idx, frame in enumerate(frames):
            
            # skip first frames if the gaps are too large
            if idx < 2:
                if frames[idx+1].frame_number - frame.frame_number > 30:
                    print(f"skipping frame {frame.frame_number}")
                    skipped_frames += 1
                    continue

            duration =  0.033
            image_url = image_lookup.get(frame.id)

            if image_url:
                concat_file.write(f"file '{log_root_path}/{image_url}'\n")
                concat_file.write(f"duration {duration}\n")

                mapping_data.append({
                    "pts": round(current_pts, 4),
                    "duration": round(duration, 4),
                    "robot_frame": frame.frame_number
                })

                # Reset the tracker for this new valid image
                last_valid_url = image_url
            else:
                print("no image on frame", frame.frame_number)
                concat_file.write(f"file '{log_root_path}/{last_valid_url}'\n")
                concat_file.write(f"duration {duration}\n")

                mapping_data.append({
                    "pts": round(current_pts, 4),
                    "duration": round(duration, 4),
                    "robot_frame": frame.frame_number
                })

            current_pts += duration

    with open(str(json_filename), "w") as json_file:
        json.dump(mapping_data, json_file, indent=2)

    return skipped_frames

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

    print(top_video_filename)

    #if bottom_video_filename.exists() and bottom_json_filename.exists():
    #    return
    #if top_video_filename.exists() and top_json_filename.exists():
    #    return

    # TODO if video exists and frames in video match continue

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

    skipped_frames = create_frame_mappings(frames, frame_count, all_top_images_generator, top_concat_file_path, top_json_filename, log_root_path)
    create_video_file(top_concat_file_path, top_video_filename, frame_count, skipped_frames)

    skipped_frames = create_frame_mappings(frames, frame_count, all_bottom_images_generator, bottom_concat_file_path, bottom_json_filename, log_root_path)
    create_video_file(bottom_concat_file_path, bottom_video_filename, frame_count, skipped_frames)

    # TODO patch log object here


def create_video_file(concat_file_path, video_filename, frame_count, skipped_frames):
    # ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0 /mnt/repl/2026_lab-tests/OrangeBallStanding/3_26_Nao0028_260114-1335/extracted/top.mp4
    if Path(video_filename).exists():
        ffprobe_cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-count_frames",
            "-show_entries", "stream=nb_read_frames",
            "-of", "csv=p=0",
            str(video_filename)
        ]
        print("Running FFProbe to count frames...")
        try:
            result= subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
            video_frame_count = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error during FFProbe execution: {e}")

        if frame_count - skipped_frames == video_frame_count:
            print("video already created with correct number of frames")
            return

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-r", "30",
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
    for log in sorted(logs, key=sort_key_fn, reverse=True):
        if log.id < 1000:
            continue
        print(log.id, log.log_path)
        create_frame_videos("/mnt/repl", client, log)
        