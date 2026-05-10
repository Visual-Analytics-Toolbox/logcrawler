from vaapi.client import Vaapi
import os
from label_studio_sdk import LabelStudio


def get_annotation(l_client,img_obj):
    task_id = img_obj.labelstudio_url.split("=")[-1]
    task = l_client.tasks.get(id=task_id)
    # there can be multiple annotations per task if multiple people annotate the same image, our images have only one annotation though
    # that's why I always take the first annotation here
    return task.annotations[0]["result"]

if __name__ == "__main__":
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    l_client = LabelStudio(
        base_url="https://labelstudio-api.berlin-united.com",
        api_key=os.environ.get("LABELSTUDIO_API_KEY"),
    )

    validated_images = v_client.image.list(validated=True)
    for img in validated_images:
        annotation = get_annotation(l_client,img)
        print(annotation)
        #v_client.image.update(annotation=annotation)
        quit()