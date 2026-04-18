from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import logging
import cv2
import os


logger = logging.getLogger(__name__)


def process_single_image(args):
    """Worker function to process a single image in a separate process."""
    img_id, img_url, log_root_path = args
    image_path = Path(log_root_path) / img_url
    
    # Read as grayscale immediately to save time/memory
    image_cv = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    
    if image_cv is None:
        return None, img_url

    try:
        brightness_value = np.average(image_cv)
        # Laplacian variance calculation
        blurredness_value = cv2.Laplacian(image_cv, cv2.CV_64F).var()
        
        return {
            "id": img_id,
            "blurredness_value": blurredness_value,
            "brightness_value": brightness_value,
        }, None
    except Exception:
        return None, img_url

def wait_and_process_futures(futures, update_list, client):
    """Helper to collect results and trigger bulk updates."""
    # This waits for at least one task to finish
    from concurrent.futures import wait, FIRST_COMPLETED
    done, pending = wait(futures, return_when=FIRST_COMPLETED)
    
    for future in done:
        result, error_url = future.result()
        if result:
            update_list.append(result)
        
        # Keep the API updates moving in chunks of 100
        if len(update_list) >= 200:
            client.image.bulk_update(data=update_list)
            update_list.clear()
            print("\tupdated 200 images")
            
    return None, pending


def calculate_image_stats(log_root_path, client, log):
    logging.info("\t\tCalculate Image Stats")
    # Define a max number of images to process at once to avoid memory bloat
    MAX_WORKERS = os.cpu_count() or 4
    BUFFER_SIZE = MAX_WORKERS * 2 

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # This is now a generator, not a list
        images_gen = client.image.list(log=log.id, blurredness_value="None")
        
        image_update_data = []
        futures = set()

        # Iterate through the paginated results without casting to list
        for img in images_gen:
            # Add a new task to the pool
            task_args = (img.id, img.image_url, log_root_path)
            futures.add(executor.submit(process_single_image, task_args))

            # If our buffer is full, process what's finished before adding more
            if len(futures) >= BUFFER_SIZE:
                done, futures = wait_and_process_futures(futures, image_update_data, client)

        # Clean up remaining futures for this log
        while futures:
            done, futures = wait_and_process_futures(futures, image_update_data, client)
        
        # Final bulk update for any leftovers in this log
        if image_update_data:
            client.image.bulk_update(data=image_update_data)




if __name__ == "__main__":
    from vaapi.client import Vaapi
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    calculate_image_stats("/mnt/repl", v_client)