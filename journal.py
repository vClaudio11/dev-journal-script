import requests
import json
from datetime import datetime, timedelta
from config import GITHUB_USERNAME, OBSIDIAN_PATH



def get_github_activity ():
    activity = {}

    # make a request
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/events"
    response = requests.get(url, headers={"User-Agent": GITHUB_USERNAME})


    # display error message if status code is not 200
    if response.status_code != 200:   
        print (f"Error retrieving data, status code: {response.status_code}")
        return {}
    
    events = response.json()

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



def display_activity(activity):
    width_outer = 40
    width_inner = 30
    total_commits = 0

    bar_char = "█"
    empty_char = "░"
    divider = "━"

    # print out activity header
    print("=" * width_outer)
    now = (datetime.now().strftime("%Y-%m-%d"))
    print(f"DEV LOG - {now}".center(width_outer))
    print("=" * width_outer)


    print("GITHUB ACTIVITY - LAST 7 DAYS")
    print(divider * width_inner)

    for date, data in activity.items():
        total_commits += data["commits"]
        commits = data["commits"]
        bar = bar_char * commits if commits > 0 else empty_char * 4
        repos = ", ".join(r.split("/")[1] for r in data["repos"]) if data["repos"] else "no repos"
        print(f"{date} {bar} {commits} commits ({repos})")
      
            

    print(f"Total this week: {total_commits} commits")
    print("=" * width_outer)


activity = get_github_activity()
display_activity(activity)