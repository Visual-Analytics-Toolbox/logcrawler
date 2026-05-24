from vaapi.client import Vaapi
import os


def test(log_root_path, client):
    def sort_key_fn(log):
        return log.id

    logs = client.logs.list()
    for log in sorted(logs, key=sort_key_fn, reverse=True):
        print(log.id)
        images = client.image.list(log=log.id)


        image_update_data = list()
        for idx, image in enumerate(images):
            json_obj = {
                "id": int(image.id),
                "log": image.frame.log,
            }
            if image.log != image.frame.log:
                image_update_data.append(json_obj)


            if idx % 200 == 0 and idx != 0 and len(image_update_data) >0:
                try:
                    response = v_client.image.bulk_update(data=image_update_data)
                    image_update_data.clear()
                    print(f"\t{idx}")

                except Exception as e:
                    #print(e)
                    print("error inputing the data")
                    quit()

        if len(image_update_data) > 0:
            try:
                response = v_client.image.bulk_update(data=image_update_data)
            except Exception as e:
                print(e)
                print("error inputing the data")
                quit()


if __name__ == "__main__":
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    test("/mnt/repl", v_client)