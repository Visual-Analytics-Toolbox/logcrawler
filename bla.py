from label_studio_sdk import LabelStudio


def fetch_all_project_counts(client: Client):
    """
    Fetches all project counts by iterating through paginated responses.

    Args:
        client: An initialized label_studio_sdk.Client instance.

    Returns:
        A list containing all LseProjectCounts objects from all pages.
    """
    all_results = []
    # Start with the initial endpoint URL
    next_url = 'api/projects/counts/'

    print(f"Starting fetch from: {next_url}")

    while next_url:
        # The client.get method will make the API call
        response = client.get(next_url)

        # Check for errors in the response structure
        if not response or 'results' not in response:
            print("Error: Invalid response format or empty response.")
            break

        # Append the results from the current page to the main list
        current_results = response.get('results', [])
        all_results.extend(current_results)

        # Get the URL for the next page
        next_url = response.get('next')

        if next_url:
            print(f"Fetched {len(current_results)} items. Moving to next page: {next_url}")
        else:
            print(f"Fetched {len(current_results)} items. Pagination complete.")

    return all_results

client = LabelStudio(
        base_url='https://labelstudio-api.berlin-united.com',  
        api_key="",
    )

fetch_all_project_counts(client)
a = client.projects.list_counts()
print(type(a))
print(a)
print()
#for i in a:
#    print(i)

existing_projects = client.projects.list()
print(type(existing_projects))
#print(len(existing_projects))