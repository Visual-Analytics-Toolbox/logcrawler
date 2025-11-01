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


def get_revision_number(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('Revision number:'):
                # Extract the value between quotes
                revision = line.split('"')[1]
                return revision
    return None  # Return None if revision number not found


def input_logs(log_root_path, client):
    games = client.games.list()
    for game in games:
        gamelog_path = Path(log_root_path) / game.game_folder / "game_logs"
        all_logs = [f for f in gamelog_path.iterdir() if f.is_dir()]

        for logfolder in sorted(all_logs):
            logfolder_parsed = str(logfolder.name).split("_")
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
                str(Path(logfolder) / "game.log")
                .removeprefix(log_root_path)
                .strip("/")
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

            try:
                response = client.logs.create(
                    game=game.id,
                    robot_version=version,
                    player_number=int(playernumber),
                    head_number=int(head_number),
                    body_serial=body_serial,
                    head_serial=head_serial,
                    log_path=log_path,
                    combined_log_path=combined_log_path,
                    sensor_log_path=sensor_log_path,
                    git_commit=hash
                )
                print(f"Created a log model with id {response.id}")
            except Exception as e:
                print("ERROR:", e)
                continue
            
            # patch game object for testgame flag
            # FIXME that should go into games
            try:
                if "test" in log_path.lower():
                    testgame_flag = True
                else:
                    testgame_flag = False

                client.games.update(
                    id=game.id,
                    is_testgame=False
                )
            except Exception as e:
                print("ERROR:", e)
                quit()

            # get log id of the newly created log object
            log_id = response.id

            # create an empty log status object here
            response = client.log_status.create(
                log=log_id,
            )