from label_studio_sdk import LabelStudio
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
        <Label value="Robot" background="#D4380D"/>
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
        <Label value="Ball" background="#FFA39E"/>
      </KeyPointLabels>
      <Text name="placeholder3" value="placeholder3">Polygon Labels</Text>
      <PolygonLabels name="polygonlabel" toName="image"
                 strokeWidth="3" pointSize="small" showInline="false">
        <Label value="Own Contour" background="red"/>
        <Label value="Line" background="blue"/>
        <Label value="Nao"/>
        <Label value="Robot"/>
        <Label value="Field Border" background="green"/>
        <Label value="Person" background="red"/>
        <Label value="Goalpost" background="#AD8B00" />
      </PolygonLabels>
    </View>
  </View>
</View>
"""

global_label_config_video = """
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

def patch_project_config(client):

    existing_projects = client.projects.list(include="id,title")
    for project in existing_projects:

        # ignore video projects for this config
        if not project.title.startswith("log"):
            continue
        print(f"updating label_config for project {project.id}")
        client.projects.update(
            id=project.id,
            label_config=global_label_config,
        )

def patch_project_config_video(client):

    existing_projects = client.projects.list(include="id,title", title="video")
    for project in existing_projects:

        # ignore video projects for this config
        if "video" not in project.title:
            continue
        print(f"updating label_config for project {project.id}")
        client.projects.update(
            id=project.id,
            label_config=global_label_config_video,
        )

def patch_project_colors(client):

    existing_projects = client.projects.list(include="id")
    for project in existing_projects:
        print(f"updating color for project {project.id}")
        client.projects.update(
            id=project.id,
            color='#CC6FBE',
        )
        

def patch_ls_webhook(client):

    existing_projects = list(client.projects.list(include="title,id"))
    for project in existing_projects:
        print(project.title)
        # FIXME only add webhook to projects starting with log_
        a = client.webhooks.list(project=project.id)
        print(f"\t{a}")

        if not a:
            print("\tTODO: create webhook")
            response = client.webhooks.create(
                url="https://vat.berlin-united.com/api/image/validate",
                headers={"Authorization": f"Token {os.environ.get('VAT_API_TOKEN')}"},
                is_active=True,
                project=project.id,
                actions=[
                    "ANNOTATION_CREATED",
                    "ANNOTATIONS_CREATED",
                    "ANNOTATION_UPDATED",
                    "ANNOTATIONS_DELETED",
                ],
                send_for_all_actions=False,
            )
            print(f"\t{response}")
        else:
            print("\twebhook already exists")
            client.webhooks.update(
                id=a[0].id,
                send_for_all_actions=False,
                actions=[
                    "ANNOTATION_CREATED",
                    "ANNOTATIONS_CREATED",
                    "ANNOTATION_UPDATED",
                    "ANNOTATIONS_DELETED",
                ],
            )


if __name__ == "__main__":
    client = LabelStudio(
        base_url="https://labelstudio-api.berlin-united.com",
        api_key=os.environ.get("LABELSTUDIO_API_KEY"),
    )
    #patch_ls_webhook(client)
    patch_project_config(client)
