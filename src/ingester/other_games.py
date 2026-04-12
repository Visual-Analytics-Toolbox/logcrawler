from typing import Dict, Mapping
from datetime import datetime
from pathlib import Path
import logging
import csv


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


def get_game_comment(game):
    if Path(game / "comments.txt").is_file():
        with open(game / "comments.txt") as f:
            comment = f.read()
    else:
        # logging.info(f"No comments.txt found for game {game.name}")
        comment = ""
    return comment


def sort_key_fn(data):
    return data.id


def input_other_games(log_root_path, client):
    logging.info("################# Input Other Game Data #################")
    events = client.events.list()
    all_teams = get_all_team_names(client)
    for event in sorted(events, key=sort_key_fn):
        ev = Path(log_root_path) / event.event_folder
        if "lab-tests" in str(event.event_folder):
            logging.debug(f"\tignoring {event.event_folder} folder for game insertion")
            continue

        file_path = ev / Path("matches.csv")

        if file_path.exists():
            with open(file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    refs = row["referees"].strip("[]")
                    timestamp_str = f"{row['date']}_{row['time'].replace(':', '-')}-00"
                    date_object = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

                    if not check_team_name(all_teams, row["team1"]):
                        logging.error(f"team {row['team1']} not found in db")
                        continue
                    if not check_team_name(all_teams, row["team2"]):
                        logging.error(f"team {row['team2']} not found in db")
                        continue

                    if row["team1"] == "Berlin United" or row["team2"] == "Berlin United":
                        logging.info("skipping inserting Berlin United games")
                        continue
                    
                    # handle half 1
                    try:
                        response = client.games.create(
                            event=event.id,
                            team1=all_teams[row["team1"]],
                            team2=all_teams[row["team2"]],
                            half="half1",
                            score=row["score"],
                            start_time=date_object.isoformat(),
                            referees=refs,
                            is_testgame=False,
                        )
                    except Exception as e:
                        logging.error(
                            f"error occured when trying to create game {row["team1"]} vs {row["team2"]} half1 : {e}"
                        )
                        continue
                    try:
                        response = client.games.update(
                            id = response.id,
                            field = row["field"],
                            referees=refs,
                            score=row["score"],
                        )
                    except Exception as e:
                        logging.error(
                            f"error occured when trying to update game {row["team1"]} vs {row["team2"]} half1 : {e}"
                        )
                        continue

                    # handle half 2
                    try:
                        response = client.games.create(
                            event=event.id,
                            team1=all_teams[row["team1"]],
                            team2=all_teams[row["team2"]],
                            half="half2",
                            score=row["score"],
                            start_time=date_object.isoformat(),
                            referees=refs,
                            is_testgame=False,
                        )
                    except Exception as e:
                        logging.error(
                            f"error occured when trying to create game {row["team1"]} vs {row["team2"]} half2 : {e}"
                        )
                        continue

                    try:
                        response = client.games.update(
                            id = response.id,
                            field = row["field"],
                            referees=refs,
                            score=row["score"],
                        )
                    except Exception as e:
                        logging.error(
                            f"error occured when trying to update game {row["team1"]} vs {row["team2"]} half2 : {e}"
                        )
                        continue
        else:
            print(f"Error: The file '{file_path}' does not exist.")
