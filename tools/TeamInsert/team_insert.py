from vaapi.client import Vaapi
import os
import yaml

if __name__ == "__main__":
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    
    event = v_client.events.list(name="2026-07-02-RC26")[0]
    
    with open('teams.yaml', 'r') as file:
        teams_data = yaml.safe_load(file)

    for team in teams_data:
        name = team['name']
        number = team['number']
    
        v_client.team.create(event=event.id, name=name, team_id=number)