from pathlib import Path
import logging


def get_robot_version(head_number: str) -> str:
    # TODO: when we have a robot model we dont need this here anymore
    head_number = int(head_number)

    if head_number > 90:
        return "v5"
    elif head_number < 40:
        return "v6"
    else:
        assert False, f"Unexpected head_number value: {head_number}"


def get_robot_id(client, body_serial):
    robot_list = client.robot.list(body_serial=body_serial)

    if not len(robot_list) == 1:
        return False
    else:
        return robot_list[0].id


def get_revision_number(file_path):
    with open(file_path, "r") as file:
        for line in file:
            if line.startswith("Revision number:"):
                # Extract the value between quotes
                revision = line.split('"')[1]
                return revision
    return None  # Return None if revision number not found


def sort_key_fn(data):
    return data.id


def input_logs(log_root_path, client):
    games = client.games.list()
    for game in sorted(games, key=sort_key_fn):
        log_folder_path = Path(log_root_path) / game.game_folder / "game_logs"

        if not log_folder_path.exists():
            logging.error(f"log folder not found at {log_folder_path}")
            continue

        all_logs = [f for f in log_folder_path.iterdir() if f.is_dir()]

        for logfolder in sorted(all_logs):
            logfolder_parsed = str(logfolder.name).split("_")

            # FIXME we only started adding the time to the folder name in 2019
            if len(logfolder_parsed) != 4:
                logging.error(
                    f"Log folder name does not match expected format {logfolder_parsed}"
                )
                continue

            playernumber = logfolder_parsed[0]
            head_number = logfolder_parsed[1]
            version = get_robot_version(head_number)
            nao_info_file = Path(logfolder) / "nao.info"

            with open(str(nao_info_file), "r") as file:
                # Read all lines from the file
                lines = file.readlines()

                # Extract the first and third lines
                body_serial = lines[
                    0
                ].strip()  # Strip to remove any trailing newline characters
                head_serial = lines[2].strip()

            log_path = (
                str(Path(logfolder) / "game.log").removeprefix(log_root_path).strip("/")
            )
            combined_log_path = (
                str(Path(logfolder) / "combined.log")
                .removeprefix(log_root_path)
                .strip("/")
            )
            sensor_log_path = (
                str(Path(logfolder) / "sensor.log")
                .removeprefix(log_root_path)
                .strip("/")
            )
            hash = get_revision_number(str(nao_info_file))
            robot_id = get_robot_id(client, body_serial)

            if not robot_id:
                logging.error(f"robot not found for body_serial {body_serial}")
                continue

            try:
                log_response = client.logs.create(
                    game=game.id,
                    player_number=int(playernumber),
                    log_path=log_path,
                    combined_log_path=combined_log_path,
                    sensor_log_path=sensor_log_path,
                    git_commit=hash,
                )
            except Exception as e:
                logging.error(f"could not create or get log object in db: {e}")
                continue

            try:
                log_response = client.logs.update(
                    id=log_response.id,
                    robot=robot_id,
                    player_number=int(playernumber),
                    log_path=log_path,
                    combined_log_path=combined_log_path,
                    sensor_log_path=sensor_log_path,
                    git_commit=hash,
                )
            except Exception as e:
                logging.error(f"could not create log object in db: {e}")
                continue

            # create an empty log status object here
            try:
                response = client.log_status.create(
                    log=log_response.id,
                )
            except Exception as e:
                logging.error(f"could not create logstatus object in db: {e} ")
                continue

            logging.info(f"created logstatus object {response}")
