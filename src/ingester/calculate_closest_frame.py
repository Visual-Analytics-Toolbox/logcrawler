from vaapi.client import Vaapi
import pandas as pd
import logging
import os


def is_done(client, log):
    num_cog_frames = client.cognitionframe.list(log=log.id, closest_motion_frame="None")
    num_mot_frames = client.motionframe.list(log=log.id, closest_cognition_frame="None")

    if num_cog_frames.count + num_mot_frames.count > 0:
        return False
    
    return True

def update_cognition_frames(client, result_cog):

    updated_frames_list = []
    for idx, row in enumerate(result_cog.itertuples()):        
        json_obj = {
            "id": row.id,
            "closest_motion_frame": row.id_motion,
        }
        updated_frames_list.append(json_obj)

        if idx % 100 == 0 and idx != 0:
            print(idx)
            try:
                response = client.cognitionframe.bulk_update(
                    data=updated_frames_list
                )
                updated_frames_list.clear()
            except Exception as e:
                print(e)
                print("error inputing the data")
                quit()

    if len(updated_frames_list) > 0:
            try:
                response = client.cognitionframe.bulk_update(data=updated_frames_list)
            except Exception as e:
                print(e)
                print("error inputing the data")
                quit()


def update_motion_frames(client, result_mot):

    updated_frames_list = []
    for idx, row in enumerate(result_mot.itertuples()):
        json_obj = {
            "id": row.id,
            "closest_cognition_frame": row.id_cognition,
        }
        updated_frames_list.append(json_obj)

        if idx % 100 == 0 and idx != 0:
            try:
                print(idx)
                response = client.motionframe.bulk_update(
                    data=updated_frames_list
                )
                updated_frames_list.clear()
            except Exception as e:
                print(e)
                print("error inputing the data")
                quit()

    if len(updated_frames_list) > 0:
            try:
                response = client.motionframe.bulk_update(data=updated_frames_list)
            except Exception as e:
                print(e)
                print("error inputing the data")
                quit()


def run_calc(client):
    logging.info("################# Calculate Closest Frames #################")
    def sort_key_fn(log):
        return log.id
    
    def sort_frames(frame):
        return frame.frame_time

    logs = client.logs.list()
    for log in sorted(logs, key=sort_key_fn):
        logging.info(f"{log.id}: {log.log_path}")

        if is_done(client, log):
            logging.info(f"\tcalculated all closest frames for {log.id} already")
            continue

        cognition_frames = sorted(list(client.cognitionframe.list(log=log.id)), key=sort_frames)
        motion_frames = sorted(list(client.motionframe.list(log=log.id)), key=sort_frames)

        clean_cog_list = [dict(frame) for frame in cognition_frames]
        clean_mot_list = [dict(frame) for frame in motion_frames]

        df_cog = pd.DataFrame(clean_cog_list)
        df_mot = pd.DataFrame(clean_mot_list)

        result_cog = pd.merge_asof(
            df_cog, 
            df_mot[['id', 'frame_time']], 
            on='frame_time', 
            direction='nearest', 
            suffixes=('', '_motion')
        )
        
        result_mot = pd.merge_asof(
            df_mot, 
            df_cog[['id', 'frame_time']], 
            on='frame_time', 
            direction='nearest', 
            suffixes=('', '_cognition')
        )

        update_cognition_frames(client, result_cog)
        update_motion_frames(client, result_mot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.ERROR)

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    run_calc(client)