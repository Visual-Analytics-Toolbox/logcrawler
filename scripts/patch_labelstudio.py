from label_studio_sdk import LabelStudio
import os

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
    patch_project_colors(client)