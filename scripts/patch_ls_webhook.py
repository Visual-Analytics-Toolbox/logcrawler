# TODO patch all projects to have webhooks
from label_studio_sdk import LabelStudio
import os


def main():
    lc = LabelStudio(
        base_url="https://labelstudio-api.berlin-united.com",
        api_key=os.environ.get("VAT_LABELSTUDIO_TOKEN"),
    )

    existing_projects = list(lc.projects.list(include="title,id"))
    for project in existing_projects:
        print(project.title)
        a = lc.webhooks.list(project=project.id)
        print(f"\t{a}")

        if not a:
            print("\tTODO: create webhook")
            response = lc.webhooks.create(
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
            lc.webhooks.update(
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
    main()
