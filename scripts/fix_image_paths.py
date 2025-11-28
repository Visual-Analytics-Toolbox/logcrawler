"""
TODO iterate over all logs and check if the test occurs in logname
"""

from label_studio_sdk import LabelStudio
from vaapi.client import Vaapi
import os


def fix_paths_labelstudio(log_id):
    existing_projects = list(lc.projects.list(title=log_id, include="title,id"))
    for p in existing_projects:
        print(p.title)
        all_tasks = lc.tasks.list(project=p.id)
        for task in all_tasks:
            if "image" in task.data:
                new_data = task.data
                new_data["image"] = task.data["image"].replace("_BHuman_", "_B-Human_")

                lc.tasks.update(
                    id=task.id,
                    data=new_data
                )


def fix_image_paths_in_db(log_id):
    images = client.image.list(log=log_id)

    updated_images = list()
    for idx, image in enumerate(images):
        
        new_url = image.image_url.replace("_BHuman_", "_B-Human_")
        #print(f"\t{new_url}")

        json_obj = {
            "id": image.id,
            "image_url": new_url,
        }
        updated_images.append(json_obj)
        if idx % 200 == 0 and idx != 0:
            print(f"{idx} - {image.image_url}")
            try:
                response = client.image.bulk_update(data=updated_images)
                updated_images.clear()
            except Exception as e:
                print(e)
                print("error inputing the data")
                quit()

    if len(updated_images) > 0:
        try:
            response = client.image.bulk_update(data=updated_images)
        except Exception as e:
            print(e)
            print("error inputing the data")
            quit()



if __name__ == "__main__":
    lc = LabelStudio(
        base_url='https://labelstudio-api.berlin-united.com',  
        api_key="",
    )

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    fix_paths_labelstudio(111)
    fix_paths_labelstudio(112)
    fix_paths_labelstudio(113)
    fix_paths_labelstudio(114)
    fix_paths_labelstudio(115)
    fix_paths_labelstudio(116)
    fix_paths_labelstudio(117)
    fix_paths_labelstudio(118)
    fix_paths_labelstudio(119)
    fix_paths_labelstudio(120)
    fix_paths_labelstudio(121)

    fix_image_paths_in_db(111)
    fix_image_paths_in_db(112)
    fix_image_paths_in_db(113)
    fix_image_paths_in_db(114)
    fix_image_paths_in_db(115)
    fix_image_paths_in_db(116)
    fix_image_paths_in_db(117)
    fix_image_paths_in_db(118)
    fix_image_paths_in_db(119)
    fix_image_paths_in_db(120)
    fix_image_paths_in_db(121)
