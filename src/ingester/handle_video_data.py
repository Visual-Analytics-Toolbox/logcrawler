from pathlib import Path
import logging


def input_videos(log_root_path, client):
    games = client.games.list(event=2)  # FIXME, should be for all events in the db but RC24 is not sorted correctly yet
    for game in games:

        game_folder = Path(log_root_path) / game.game_folder
        
        video_folder = Path(game_folder) / "videos"
        if not video_folder.exists():
            logging.debug(f"video folder does not exist for {game} - {video_folder}")
            continue

        all_videos = [f for f in video_folder.iterdir()]

        for video in all_videos:
            # parse the video file name
            video_path = str(video).removeprefix(log_root_path).strip("/")
            video_parsed = str(video.name).split("_")
            # TODO: assert that the video name is names correctly
            video_type = Path(video_parsed[7]).stem  # removes the .mp4 ending
            
            # TODO add youtube urls
            try:
                response = client.video.create(game=game.id, video_path=video_path, type=str(video_type))
            except Exception as e:
                logging.error(f"error occured when trying to insert game {game.name}:{e}")
