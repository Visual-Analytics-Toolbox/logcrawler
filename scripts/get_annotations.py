from vaapi.client import Vaapi
import os
from label_studio_sdk import LabelStudio


def get_annotation(l_client,img_obj):
    task_id = img_obj.labelstudio_url.split("=")[-1]
    task = l_client.tasks.get(id=task_id)
    # there can be multiple annotations per task if multiple people annotate the same image, our images have only one annotation though
    # that's why I always take the first annotation here
    if len(task.annotations) == 0:
        return None
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

    validated_images = list(v_client.image.list(has_annotations=True, annotation=None))
    print(len(validated_images))

    for idx, img in enumerate(validated_images):
        #print(idx)
        if len(img.annotation) > 0:
            continue
        print(img)
        v_client.image.update(id=img.id, has_annotations=False, annotation=None)
        """
        quit()
        annotation = get_annotation(l_client,img)
        # dont copy empty annotations and set the has_annotations to False
        if not annotation:
            v_client.image.update(id=img.id, has_annotations=False, annotation=None)

            continue

        if isinstance(img.annotation, list):
            continue
        
        print(img)
        print(annotation)
        v_client.image.update(id=img.id, annotation=annotation)
        """
