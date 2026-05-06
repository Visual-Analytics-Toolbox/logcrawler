from label_studio_sdk import LabelStudio
from vaapi.client import Vaapi
import math
import os
import re

def sort_key_fn(data):
    return data.id


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(l, key=alphanum_key)


def main(v_client, l_client):
    logs = v_client.logs.list()

    project_names = list()
    for log in sorted(logs, key=sort_key_fn):
        print(log.id)
        
        image_count_top = v_client.image.get_image_count(log=log.id, camera="TOP")["count"]
        image_count_bottom = v_client.image.get_image_count(log=log.id, camera="BOTTOM")["count"]

        num_projects_top = math.ceil(image_count_top / 1000)
        num_projects_bottom = math.ceil(image_count_bottom / 1000)
        for a in range(num_projects_top):
            project_names.append(f"log-{log.id}_part-{a}_top")
        
        for a in range(num_projects_bottom):
            project_names.append(f"log-{log.id}_part-{a}_bottom")

    print("fetch existing project names")
    existing_projects = list(l_client.projects.list(include="title"))
    existing_project_titles = [p.title for p in existing_projects]

    print("find missing projects")
    for name in natural_sort(project_names):
        if name in existing_project_titles:
            continue
        else:
            print(f"Project {name} is missing in labelstudio")


if __name__ == "__main__":
    l_client = LabelStudio(
        base_url="https://labelstudio-api.berlin-united.com",
        api_key=os.environ.get("LABELSTUDIO_API_KEY"),
    )

    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    main(v_client, l_client)
    