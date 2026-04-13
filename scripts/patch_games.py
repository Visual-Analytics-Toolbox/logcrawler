from pathlib import Path
from datetime import datetime
from vaapi.client import Vaapi
import logging
import os


def test2(log_root_path, client):
    logs = client.logs.list(game=96)
    for log in logs:
        print(log.id)
        if log.sensor_log_path != log.sensor_log_path.replace("_17-15-00_", "_17-30-00_"):
            client.logs.update(id=log.id, sensor_log_path=log.sensor_log_path.replace("_17-15-00_", "_17-30-00_"))

        



def test(log_root_path, client):
    logs = client.logs.list(game=96)
    for log in logs:
        images = client.image.list(log=log.id)
        print(log.id)
        image_update_data = list()
        for idx, image in enumerate(images):

            json_obj = {
                "id": int(image.id),
                "image_url": image.image_url.replace("_17-15-00_", "_17-30-00_"),
            }
            if image.image_url != image.image_url.replace("_17-15-00_", "_17-30-00_"):
                image_update_data.append(json_obj)

            if idx % 100 == 0 and idx != 0 and len(image_update_data) >0:
                try:
                    response = v_client.image.bulk_update(data=image_update_data)
                    image_update_data.clear()
                    print(idx)
                except Exception as e:
                    print(e)
                    print("error inputing the data")
                    quit()

        if len(image_update_data) > 0:
            try:
                response = v_client.image.bulk_update(data=image_update_data)
            except Exception as e:
                print(e)
                print("error inputing the data")
                quit()


if __name__ == "__main__":
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    test2("/mnt/repl", v_client)