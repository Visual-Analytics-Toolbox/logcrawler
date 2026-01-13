"""
We have multiple cases to handle in case of lab-tests

2025_lab-test/
- 2025_03_04_16_00_00-Testspiel_2v2 -> experiment name
  - 1_31_Nao0025_250304-1457
  - 4_34_Nao0021_250304-1457
- NewBall
  - newBall.log
- nao34_ball_lost.log (this case will be ignored for now)
The same structure could be happening in each events experiment folder

FIXME: there are still subfolders that contain multiple experiments. Those should go into there own folders
"""


from pathlib import Path
import logging


def sort_key_fn(data):
    return data.id


def input_experiments(log_root_path, client):
    events = client.events.list()
    for event in events:
        ev = Path(log_root_path) / event.event_folder
        all_games = [f for f in ev.iterdir() if f.is_dir()]
        for game in sorted(all_games):
            logging.debug(f"parsing folder {game}")
            if str(game.name) != "Experiments":
                continue

            # TODO handle experiments logic here

def input_lab_experiments(log_root_path, client):
    logging.info("################# Input Experiment Data #################")
    events = client.events.list()
    for event in sorted(events, key=sort_key_fn):
        ev = Path(log_root_path) / event.event_folder
        if "lab-tests" in str(event.event_folder):
            # ignoring log files not inside a subfolder
            all_experiments = [f for f in ev.iterdir() if f.is_dir()]
            for experiment in sorted(all_experiments):
                logging.info(f"\t{experiment.name}")
                # TODO figure out the experiment type
                has_log_files = any(experiment.glob("*.log"))
                logging.info(f"\t\thas log files:{has_log_files}")
                # TODO: add function to handle_logs for each experiment of type game.log
                try:
                    response = client.experiment.create(
                        event=event.id,
                        name=experiment.name,
                        type="Simple" if has_log_files else "Gamelog",
                    )
                    logging.debug(f"successfully inserted {experiment.name} in db")
                except Exception as e:
                    logging.error(
                        f"error occured when trying to insert experiment {experiment.name}:{e}"
                    )