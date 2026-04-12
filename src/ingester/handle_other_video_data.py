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


def input_other_video_data(log_root_path, client):
    events = client.events.list()
    all_teams = get_all_team_names(client)
    for event in events:
        #if event.id != 10:
        #    continue
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
            #print(video_parsed)
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