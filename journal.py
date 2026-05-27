import requests
import json
from datetime import datetime, timedelta
from config import GITHUB_USERNAME, OBSIDIAN_PATH

def get_github_activity ():
    activity = {}

    # make a request
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/events"
    response = requests.get(url, headers={"User-Agent": GITHUB_USERNAME})
    
    print(f"Status code: {response.status_code}")
    print(f"Number of events: {len(response.json())}")


    # display error message if status code is not 200
    if response.status_code != 200:   
        print (f"Error retrieving data, status code: {response.status_code}")
        return {}
    
    events = response.json()
    print(response.status_code)
    print(json.dumps(events[0], indent=2))

    # build activity dictionary for the questions
    today = datetime.now().date()
    for i in range(7):
        day = today - timedelta(days= i)
        activity[str(day)] = {"commits": 0, "repos": set()}

    # loop through events and only check for git pushes to repo
    for event in events:
        # check if event is a push event - ignore the rest
        if event["type"] == "PushEvent":
            date = event["created_at"][:10]
            if date in activity:
                commits = event["payload"].get("commits", [])
                activity[date]["commits"] += len(commits)
                activity[date]["repos"].add(event["repo"]["name"])

    return activity

print(get_github_activity())