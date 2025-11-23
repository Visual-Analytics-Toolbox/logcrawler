from label_studio_sdk import LabelStudio
from vaapi.client import Vaapi
import collections
import time
import os

global_label_config = """
<View>
  <Markdown value="$markdown_description"/>
  <View style="display:flex;align-items:start;gap:8px;flex-direction:row">
    <Image name="image" value="$image" zoomControl="true" zoom="true"/>
    <View style="display:flex;align-items:start;gap:8px;flex-direction:column">
      <Text name="placeholder1" value="placeholder1">BBox Labels</Text>
      <RectangleLabels name="label" toName="image" showInline="false">
        <Label value="Ball" background="#FFA39E"/>
        <Label value="Nao" background="#D4380D"/>
        <Label value="Person" background="#FFC069"/>
        <Label value="Referee" background="#AD8B00"/>
        <Label value="Penalty Mark" background="#AD8B00"/>
      </RectangleLabels>
      <Text name="placeholder2" value="placeholder2">Keypoint Labels</Text>
      <KeyPointLabels name="kp-1" toName="image" showInline="false" strokeWidth="7">
        <Label value="Goalpost" background="blue" />
        <Label value="T Cross" background="blue" />
        <Label value="Center Cross" background="blue" />
        <Label value="Circle Cross" background="blue" />
        <Label value="L Cross" background="blue" />
      </KeyPointLabels>
      <Text name="placeholder3" value="placeholder3">Polygon Labels</Text>
      <PolygonLabels name="polygonlabel" toName="image"
                 strokeWidth="3" pointSize="small" showInline="false">
        <Label value="Own Contour" background="red"/>
        <Label value="Line" background="blue"/>
        <Label value="Nao"/>
        <Label value="Field Border" background="green"/>
        <Label value="Person" background="red"/>
      </PolygonLabels>
    </View>
  </View>
</View>
"""

view_config = {
    "title":"Default",
    "hiddenColumns":{
        "explore":[
            "tasks:inner_id",
            "tasks:annotations_results",
            "tasks:annotations_ids",
            "tasks:predictions_score",
            "tasks:predictions_model_versions",
            "tasks:predictions_results",
            "tasks:file_upload",
            "tasks:storage_filename",
            "tasks:created_at",
            "tasks:updated_at",
            "tasks:updated_by",
            "tasks:avg_lead_time",
            "tasks:draft_exists"
        ],
        "labeling":[
            "tasks:data.markdown_description",
            "tasks:id",
            "tasks:inner_id",
            "tasks:completed_at",
            "tasks:cancelled_annotations",
            "tasks:total_predictions",
            "tasks:annotators",
            "tasks:annotations_results",
            "tasks:annotations_ids",
            "tasks:predictions_score",
            "tasks:predictions_model_versions",
            "tasks:predictions_results",
            "tasks:file_upload",
            "tasks:storage_filename",
            "tasks:created_at",
            "tasks:updated_at",
            "tasks:updated_by",
            "tasks:avg_lead_time",
            "tasks:draft_exists"
        ]
    },
}

def get_images_per_log(v_client, log_id, camera):
    image_generator = v_client.image.list(log=log_id, camera=camera)
    image_list = sorted(list(image_generator), key=lambda x: x.frame.frame_number)

    return image_list


def calculate_project_names(log_id, image_list, camera):
    project_names = list()
    for idx, image in enumerate(image_list):
        project_name = f"log-{log_id}_part-{idx // 1000}_{camera.lower()}"
        project_names.append(project_name)

    return set(project_names)


def create_project_if_not_exist(client, project_names):
    existing_projects = list(client.projects.list())
    existing_project_titles = [p.title for p in existing_projects]
    for name in sorted(project_names):
        if name in existing_project_titles:
            continue
        else:
            project = client.projects.create(
                title=name,
                label_config=global_label_config
            )
            time.sleep(2)
            client.views.create(project=project.id, data=view_config)


def import_image_tasks_faster(client, v_client, log_id, image_list, camera):
    # 1. Pre-calculate all needed project names and their IDs
    print("Pre-fetching project IDs...")
    existing_projects = list(client.projects.list())
    
    # Create a mapping from project_name to project_id
    project_map = {}
    for idx, image in enumerate(image_list):
        # The project name logic is based on idx:
        project_name = f"log-{log_id}_part-{idx // 1000}_{camera.lower()}"
        
        if project_name not in project_map:
            # Find the ID for the project name and store it
            try:
                project_id = next(p.id for p in existing_projects if p.title == project_name)
                project_map[project_name] = project_id
            except StopIteration:
                print(f"Warning: Project {project_name} not found. Skipping related images.")
                # You might want to handle this differently, e.g., create the project
                project_map[project_name] = None # Mark as not found to skip later

    # 2. Fetch all existing task URLs for all relevant projects in a batch
    print("Pre-fetching existing task URLs...")
    # Get all unique project IDs that were found
    relevant_project_ids = set(pid for pid in project_map.values() if pid is not None)
    
    # Structure to hold existing URLs: project_id -> set of image_urls
    existing_task_urls = collections.defaultdict(set)
    
    for project_id in relevant_project_ids:
        # Fetch tasks for this project (API call outside the main loop)
        all_tasks = client.tasks.list(project=project_id) 
        
        # Build the set for efficient O(1) lookup inside the loop
        for task in all_tasks:
            if "image" in task.data:
                existing_task_urls[project_id].add(task.data["image"])

    # 3. Iterate over images, perform efficient checks, and create/update
    print("Processing images...")
    base_url = "https://logs.berlin-united.com/"
    
    # Pre-fetch views for projects to avoid repeated calls later
    view_map = {}
    for project_id in relevant_project_ids:
        view_map[project_id] = client.views.list(project=project_id)[0]

    for idx, image in enumerate(image_list):
        # Calculate project name and get ID from pre-calculated map (O(1) lookup)
        project_name = f"log-{log_id}_part-{idx // 1000}_{camera.lower()}"
        project_id = project_map.get(project_name)

        if project_id is None:
            # Skip if project wasn't found in step 1
            continue

        image_full_url = f"{base_url}{image.image_url}"

        # **FAST CHECK:** Use the pre-fetched set for O(1) lookup
        if image_full_url in existing_task_urls.get(project_id, set()):
            # Image already exists in this project's tasks, skip
            continue

        # Create Task (API call)
        task = client.tasks.create(
            project=project_id,
            data={"image": image_full_url, "markdown_description": f"Log Url: [https://vat.berlin-united.com/api/images/{image.id}](https://vat.berlin-united.com/api/images/{image.id})"}
        )

        # Update Image URL (API call)
        view = view_map[project_id] # O(1) lookup from pre-fetched map
        v_client.image.update(
            id=image.id,
            labelstudio_url=f"https://labelstudio.berlin-united.com/projects/{project_id}/data?tab={view.id}&task={task.id}"
        )
        print(f"Imported task for index {idx}. Task ID: {task.id}")

    print("Import complete.")


def import_image_tasks(client, v_client, log_id, image_list, camera):
    existing_projects = list(client.projects.list())

    for idx, image in enumerate(image_list):
        print(idx)
        project_name = f"log-{log_id}_part-{idx // 1000}_{camera.lower()}"
        project_id = [p.id for p in existing_projects if p.title == project_name][0]

        # TODO check if image url is already in list of tasks (would require a tasks.list in every iteration)
        all_tasks = list(client.tasks.list(project=project_id))
        if len(all_tasks) > 0:
            all_image_urls = [imgurl.data["image"] for imgurl in all_tasks]
            if f"https://logs.berlin-united.com/{image.image_url}" in all_image_urls:
                continue

        task = client.tasks.create(
            project=project_id,
            data={"image": f"https://logs.berlin-united.com/{image.image_url}", "markdown_description": f"Log Url: [https://vat.berlin-united.com/api/images/{image.id}](https://vat.berlin-united.com/api/images/{image.id})"}
        )

        view = client.views.list(project=project_id)[0]
        v_client.image.update(
            id = image.id,
            labelstudio_url = f"https://labelstudio.berlin-united.com/projects/{project_id}/data?tab={view.id}&task={task.id}"
        )


def main():
    client = LabelStudio(
        base_url='https://labelstudio-api.berlin-united.com',  
        api_key="",
    )

    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    logs = v_client.logs.list()

    for log in sorted(logs, key=lambda x: x.id):
        if log.id > 40:
            break
        print(f"handling log {log.id}")
        for camera in ["BOTTOM", "TOP"]:
            image_list = get_images_per_log(v_client, log.id, camera)
            print(f"\tnum images: {len(image_list)}")
            project_names = calculate_project_names(log.id, image_list, camera)
            create_project_if_not_exist(client, project_names)
            import_image_tasks_faster(client, v_client, log.id, image_list, camera)


if __name__ == "__main__":
    main()
