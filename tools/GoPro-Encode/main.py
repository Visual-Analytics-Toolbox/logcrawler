import subprocess
from pathlib import Path
from telemetry_parser import Parser as GPMFParser


def is_already_reencoded(filepath):
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


def process_video(input_path):
    # Create output path (modify as needed)
    output_path = video_input.replace("_GoPro", "_GoPro_reencoded")

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
    tele = GPMFParser(output_path).telemetry()
    print(len(tele))


video_list = [
    "/mnt/d/logs/2025-03-12-GO25/videos/2025-03-13_10-00-00_B-Human_vs_HTWK Robots_half1_Field-A_GoPro.mp4",
    "/mnt/d/logs/2025-03-12-GO25/videos/2025-03-13_10-00-00_B-Human_vs_HTWK Robots_half1_Field-A_GoPro2.mp4",
]


for video_input in video_list:
    encoded = is_already_reencoded(video_input)
    if not encoded:
        process_video(video_input)
