from pathlib import Path
import logging


def get_comments(current_folder):
    if Path(current_folder / "comments.txt").is_file():
        with open(current_folder / "comments.txt") as f:
            comment = f.read()
    else:
        logging.warning(f"No comments.txt found for game {current_folder.name}")
        comment = ""
    return comment


def input_videos(log_root_path, client):
    games = client.games.list()
    for game in games:
        game_folder = Path(log_root_path) / game.game_folder

        video_folder = Path(game_folder) / "videos"
        if not video_folder.exists():
            logging.debug(f"video folder does not exist for {game} - {video_folder}")
            continue

        all_videos = [f for f in video_folder.iterdir() if f.suffix.lower() == ".mp4"]
        for video in all_videos:
            # parse the video file name
            video_path = str(video).removeprefix(log_root_path).strip("/")

            if Path(video_path).suffix != ".mp4":
                logging.error(
                    f"Video file name does not match expected format {video_path}"
                )
                continue

            video_parsed = str(video.name).split("_")
            if len(video_parsed) != 8:
                logging.error(
                    f"Video file name does not match expected format {video_path}"
                )
                continue

            # FIXME check that the parsed team names are actually team names

            # either GoPro or PiCam
            video_type = Path(video_parsed[7]).stem  # removes the .mp4 ending

            try:
                response = client.video.create(
                    game=game.id, video_path=video_path, type=str(video_type)
                )
            except Exception as e:
                logging.error(
                    f"error occured when trying to insert video  {video_path}:{e}"
                )
                continue

            # TODO add urls with patch here
            comments = get_comments(video_folder)
            try:
                response = client.video.update(
                    id=response.id,
                    comment=comments,
                )
            except Exception as e:
                logging.error(
                    f"error occured when trying to insert game {video_path}:{e}"
                )
