from label_studio_sdk import LabelStudio
from collections import defaultdict
from vaapi.client import Vaapi
from urllib.parse import quote
from pathlib import Path
import os


global_label_config = """
<View>
  <Markdown value="$markdown_description"/>
  
  <View style="display: flex; flex-direction: row; gap: 20px; align-items: flex-start; width: 100%;">
    
    <View style="flex: 1; min-width: 0; overflow: hidden;">
      <Video name="video" value="$video" />
    </View>

    <View style="flex: 0 0 200px; position: sticky; top: 0;">
      <Labels name="videoLabels" toName="video">
        <Label value="Ball" background="#FFA39E"/>
        <Label value="Nao" background="#D4380D"/>
        <Label value="Robot" background="#D4380D"/>
        <Label value="Person" background="#FFC069"/>
        <Label value="Referee" background="#AD8B00"/>
      </Labels>
      <View visibleWhen="region-selected" 
            whenTagName="videoLabels" 
            whenLabelValue="Nao,Robot">
        <Header value="Assign ID / Player Number" size="6" />
        <TextArea name="player_id" toName="video" 
                  editable="true" 
                  perRegion="true" 
                  placeholder="e.g. Player 3" />
      </View>
    </View>
  </View>
  <VideoRectangle name="box" toName="video" />
</View>
"""

view_config = {
    "title": "Default",
    "hiddenColumns": {
        "explore": [
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
            "tasks:draft_exists",
        ],
        "labeling": [
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
            "tasks:draft_exists",
        ],
    },
}

def sort_key_fn(data):
    return data.id

def run_labelstudio_insert_videos():
    client = LabelStudio(
        base_url="https://labelstudio-api.berlin-united.com",
        api_key=os.environ.get("LABELSTUDIO_API_KEY"),
    )

    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    existing_projects = list(client.projects.list(include="title,id", title="video"))
    existing_project_titles = [p.title for p in existing_projects]

    # TODO get all game id from all events
    events = v_client.events.list(is_testevent=False)
    for event in events:
        project_name = f"{event.name}_videos"
        print(f"\tcreate project {project_name} if_not_exist")
        

        if project_name not in existing_project_titles:
            project = client.projects.create(
                title=project_name, label_config=global_label_config
            )
            client.views.create(project=project.id, data=view_config)
            project_id = project.id
        else:
            project_id = [p.id for p in existing_projects if p.title == project_name][0]

        print("project_id", project_id)
        if event.id != 10:
            continue
        
        existing_task_urls = defaultdict(set)
        all_tasks = client.tasks.list(project=project_id, include="data")
        for task in all_tasks:
            if "video" in task.data:
                existing_task_urls[project_id].add(task.data["video"])
        
        games = v_client.games.list(event=event.id)
        for game in sorted(games, key=sort_key_fn):
            # check if video exist
            videos = v_client.videos.list(game=game.id)
            if len(videos) == 0:
                continue

            # FIXME choose a video if two are available
            video = videos[0]

            if f"https://logs.berlin-united.com/{video.video_path}" in existing_task_urls.get(project_id, set()):
                # video already exists in this project's tasks, skip
                continue

            safe_path = quote(video.video_path)
            task_data = {
                "video": f"https://logs.berlin-united.com/{video.video_path}",
                "markdown_description": f"Video: [https://vat.berlin-united.com/api/video/{video.id}](https://vat.berlin-united.com/api/video/{video.id})  \n Raw: [{Path(video.video_path).name}](https://logs.berlin-united.com/{safe_path})",
            }
            resp = client.projects.import_tasks(
                id=project_id,
                request=task_data,
                return_task_ids=True,
            )

run_labelstudio_insert_videos()