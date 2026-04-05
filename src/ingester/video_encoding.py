from telemetry_parser import Parser as GPMFParser
from vaapi.client import Vaapi
from pathlib import Path
import subprocess
import json
import os


def get_video_stream_info(file_path):
    """Returns the first video stream's metadata."""
    cmd = [
        "ffprobe", "-v", "error", 
        "-select_streams", "v:0", 
        "-show_entries", "stream=avg_frame_rate,r_frame_rate,nb_frames,codec_name", 
        "-of", "json", file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        print(f"\t{data}")
        return data['streams'][0]
    except (subprocess.CalledProcessError, IndexError, KeyError):
        return None


def gopro_is_already_reencoded(filepath):
    cmd = [
        "ffprobe", "-v", "error", 
        "-select_streams", "v:0", 
        "-show_entries", "stream_tags=encoder", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        str(filepath)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # If "gopro" is in the encoder tag, we have to encode the video
    encoded = "gopro" not in result.stdout.lower()
    return encoded


def process_gopro_video(input_path):
    # Create output path (modify as needed)
    output_path = input_path.replace("_GoPro", "_GoPro_reencoded")

    if Path(output_path).exists():
        return
    # FFmpeg command
    cmd = [
        "ffmpeg",
        "-i",
        input_path,
        "-map",
        "0:v",
        "-map",
        "0:a",
        "-map",
        "0:3",
        "-c:v",
        "libx264",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-c:s",
        "copy",
        "-c:d",
        "copy",
        "-movflags",
        "+faststart",
        output_path,
    ]

    try:
        # Run the command
        subprocess.run(cmd, check=True)
        print(f"Successfully processed {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {input_path}: {e}")
        quit()

    # TODO test telemetry
    telemetry_data = GPMFParser(output_path).telemetry()
    print(f"\tnum telemetrie data output: {len(telemetry_data)}")


def encode_gopro_videos(log_root_path, client):
    videos = client.videos.list(type="GoPro")
    for video in videos:
        print(video)

        video_path = Path(log_root_path) / video.video_path

        info = get_video_stream_info(video_path)
        if not info:
            print(f"Skipping {video_path}: Could not read video info.")
            continue

        if not info.get('avg_frame_rate') == info.get('r_frame_rate'):
            print(f"Skipping {video_path}: Framerate is not constant")
            continue

        encoded = gopro_is_already_reencoded(video_path)
        if encoded:
            print(f"Skipping {video_path}: Video is already reencoded")
            continue
        
        telemetry_data = GPMFParser(str(video_path)).telemetry()
        print(f"\tnum telemetrie data input: {len(telemetry_data)}")

        process_gopro_video(str(video_path))


if __name__ == "__main__":
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    encode_gopro_videos("/mnt/repl", v_client)