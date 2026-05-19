from vaapi.client import Vaapi
from pathlib import Path
import subprocess
import logging
import os
import re


logger = logging.getLogger(__name__)

def is_done():
    pass

def create_frame_videos(log_root_path, client, log):
    log_path = Path(log_root_path) / Path(log.combined_log_path)
    #print(log_path)
    if not log.game:
        extracted_folder = str(log_path.parent / "extracted")
    else:
        extracted_folder = str(log_path.parent).replace("game_logs", "extracted")
    #print(extracted_folder)

    bottom_folder = Path(extracted_folder) / "log_bottom_jpg"
    top_folder = Path(extracted_folder) / "log_top_jpg"
    # abort if no jpeg logs
    if not bottom_folder.exists():
        return
    if not top_folder.exists():
        return

    # TODO get the number of frames and number of images per camera - abort if the ratio is off
    frame_count = client.cognitionframe.get_frame_count(log=log.id)["count"]
    bottom_image_count = client.image.get_image_count(log=log.id, camera="BOTTOM")["count"]
    top_image_count = client.image.get_image_count(log=log.id, camera="TOP")["count"]
    print(log.id, frame_count, bottom_image_count, top_image_count, top_image_count/frame_count)

    if top_image_count/frame_count < 0.97:
        return    
    if bottom_image_count/frame_count < 0.97:
        return
    
    return

def create_video_from_frames(image_folder, output_file, fps=30):
    # 1. Get all files and sort them by frame number
    pattern = re.compile(r'(\d+)')
    files = {}
    
    for f in os.listdir(image_folder):
        match = pattern.search(f)
        if match:
            files[int(match.group(1))] = f

    if not files:
        print("No images found!")
        return

    frame_numbers = sorted(files.keys())
    first_frame = frame_numbers[0]
    last_frame = frame_numbers[-1]
    
    # Duration per frame (1/30 = 0.033333)
    frame_duration = 1.0 / fps

    # 2. Generate the instructions for FFmpeg
    concat_file = "inputs.txt"
    with open(concat_file, "w") as f:
        current_img = files[first_frame]
        accumulated_duration = 0.0

        for nr in range(first_frame, last_frame + 1):
            if nr in files:
                # If we have a previous image pending, write it now
                if accumulated_duration > 0:
                    f.write(f"file '{os.path.join(image_folder, current_img)}'\n")
                    f.write(f"duration {accumulated_duration}\n")
                
                # Update to the new current image
                current_img = files[nr]
                accumulated_duration = frame_duration
            else:
                # Frame is missing! Add duration to the last known image
                accumulated_duration += frame_duration

        # Write the very last frame
        f.write(f"file '{os.path.join(image_folder, current_img)}'\n")
        f.write(f"duration {accumulated_duration}\n")

    # 3. Run FFmpeg
    # -safe 0 allows absolute paths, -y overwrites output
    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', 
        '-i', concat_file, 
        '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', 
        output_file
    ]
    
    subprocess.run(cmd)
    os.remove(concat_file) # Clean up
    print(f"Video saved to {output_file}")

# Usage
#create_video_from_frames('/mnt/d/logs/2026-03-10-GO26/2026-03-14_13-10-00_Berlin United_vs_R-ZWEI KICKERS_half2/extracted/4_31_Nao0025_260314-1310/log_top_jpg', 'robot_log_fixed.mp4')

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
