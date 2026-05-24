import subprocess
from naoth.log import Reader as LogReader
from PIL import Image as PIL_Image
from naoth.log import Parser
import numpy as np
import json
import io


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


def create_top_video():
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
        str("top.mp4")
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    last_valid_frame = None
    mapping_data = []
    current_pts = 0.0
    duration =  0.033
    with LogReader("combined.log", my_parser) as reader:
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

    with open(str("top.json"), "w") as json_file:
        json.dump(mapping_data, json_file, indent=2)

def create_bottom_video():
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
        str("bottom.mp4")
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    last_valid_frame = None
    mapping_data = []
    current_pts = 0.0
    duration =  0.033
    with LogReader("combined.log", my_parser) as reader:
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
    with open(str("bottom.json"), "w") as json_file:
        json.dump(mapping_data, json_file, indent=2)

def create_videos():
    create_top_video()
    create_bottom_video()

if __name__ == "__main__":
    create_videos()