from pathlib import Path
import numpy as np
import cv2


def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


def calculate_image_stats(log_root_path, client):
    logs = client.logs.list()

    def sort_key_fn(log):
        return log.id

    for log in sorted(logs, key=sort_key_fn, reverse=True):
        print(f"{log.id}: {log.log_path}")

        images = client.image.list(log=log.id, blurredness_value="None")

        image_update_data = list()
        for idx, img in enumerate(images):
            image_path = Path(log_root_path) / img.image_url
            image_cv = cv2.imread(image_path, cv2.IMREAD_COLOR)

            try:
                gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
                brightness_value = np.average(gray)
                blurredness_value = variance_of_laplacian(gray)

                json_obj = {
                    "id": img.id,
                    "blurredness_value": blurredness_value,
                    "brightness_value": brightness_value,
                }

                image_update_data.append(json_obj)

            except Exception as e:
                print(e)
                print(f"Image broken at {img.image_url} in log: {log.id}")
                print(
                    "This problem can occur if the image extraction for this log was aborted"
                )
                quit()

            if idx % 100 == 0 and idx != 0:
                try:
                    response = client.image.bulk_update(data=image_update_data)
                    image_update_data.clear()
                    print(idx)
                except Exception as e:
                    print(e)
                    print("error inputing the data")
                    quit()

        if len(image_update_data) > 0:
            try:
                response = client.image.bulk_update(data=image_update_data)
            except Exception as e:
                print(e)
                print("error inputing the data")
                quit()
