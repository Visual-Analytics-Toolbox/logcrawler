from typing import Dict, Mapping
from vaapi.client import Vaapi
from pathlib import Path
import logging
import os


def get_all_team_names(client) -> Dict[str, int]:
    """
    Get a list of team names from the db
    """
    return {team.name: team.id for team in client.team.list()}


def check_team_name(all_teams: Mapping[str, int], team_name: str) -> bool:
    """
    Check if the name of the team that should be inserted matches the spelling of the team name in the db
    """
    return team_name in all_teams.keys()


def get_comments(current_folder):
    if Path(current_folder / "comments.txt").is_file():
        with open(current_folder / "comments.txt") as f:
            comment = f.read()
    else:
        # logging.info(f"No comments.txt found for game {current_folder.name}")
        comment = ""
    return comment


def input_videos(log_root_path, client):
    logging.info("################# Input Our Video Data #################")
    games = client.games.list()
    for game in games:
        if not game.game_folder:
            logging.debug(f"skipping - this is a game without a game_folder - proably game without us playing")
            continue

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
                response = client.videos.create(
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
                response = client.videos.update(
                    id=response.id,
                    comment=comments,
                )
            except Exception as e:
                logging.error(
                    f"error occured when trying to insert game {video_path}:{e}"
                )


def input_other_video_data(log_root_path, client):
    logging.info("################# Input Other Video Data #################")
    events = client.events.list()
    all_teams = get_all_team_names(client)
    for event in events:
        video_folder = Path(log_root_path) / event.event_folder / "videos"
        
        if not video_folder.exists():
            logging.debug(f"video folder for event {event.name} does not exist - {video_folder}")
            continue

        all_videos = [f for f in video_folder.iterdir() if f.suffix.lower() == ".mp4"]
        for video in all_videos:
             # parse the video file name
            video_path = str(video).removeprefix(log_root_path).strip("/")

            video_parsed = str(video.name).split("_")
            if len(video_parsed) != 8:
                logging.error(
                    f"Video file name does not match expected format {video_path}"
                )
                continue

            timestamp_str = video_parsed[0] + "_" + video_parsed[1]
            video_half = video_parsed[5]
            video_type = Path(video_parsed[7]).stem  # removes the .mp4 ending

            if not check_team_name(all_teams, video_parsed[2]):
                logging.error(f"team {video_parsed[2]} not found in db - {video_parsed}")
                continue
            if not check_team_name(all_teams, video_parsed[4]):
                logging.error(f"team {video_parsed[4]} not found in db - {video_parsed}")
                continue
            
            # find a game for the video
            # FIXME use teams here as well for filtering - build something that can filter games by team first
            game_list = client.games.list(event=event.id, game_folder=None, start_time=timestamp_str, half=video_half)
            if not game_list:
                # FIXME this happens for timout parts and penalty shoot outs - create the games for this in this case
                logging.error(f"no game found for video {video_parsed}")
                continue
            
            if len(game_list) > 1:
                logging.error(f"somehow found two games for {video_parsed}")
                continue

            game = game_list[0]
            try:
                response = client.videos.create(
                    game=game.id, video_path=video_path, type=str(video_type)
                )
            except Exception as e:
                logging.error(
                    f"error occured when trying to insert video  {video_path}:{e}"
                )
                continue


if __name__ == "__main__":
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    input_other_video_data("/mnt/repl", v_client)