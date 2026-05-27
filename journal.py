import requests
from pathlib import Path
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
    
    width_outer = 80
    width_inner = 70
    total_commits = 0
    max_bar = 15

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
        data["commits"] = 0
        for repo in data["repos"]:
            commits_url = f"https://api.github.com/repos/{repo}/commits"
            params = {
                "since": f"{date}T00:00:00Z",
                "until": f"{date}T23:59:59Z"
            }

            commits_response = requests.get(
                commits_url,
                headers={"User-Agent" : GITHUB_USERNAME},
                params=params
            )

            if commits_response.status_code == 200:
                activity[date]["commits"] += len(commits_response.json())

        total_commits += data["commits"]
        commits = data["commits"]
        bar = bar_char * min(commits, max_bar) if commits > 0 else empty_char * 4
        repos = ", ".join(r.split("/")[1] for r in data["repos"]) if data["repos"] else "no repos"
        print(f"{date:<12} {bar:<15} {commits:>3} commits ({repos})")
      
            

    print(f"Total this week: {total_commits} commits")
    print("=" * width_outer)



def get_journal_input():

    width = 80
    user_work = input("What did you work on today? >")
    user_learn = input("What did you learn today? >")
    user_tomorrow = input("What's next for tomorrow? >")
    user_blockers = input("Any blockers? >") or "None"

    answers = {
        "worked_on" : user_work, 
        "learned" : user_learn,
        "tomorrow" : user_tomorrow,
        "blockers" :user_blockers 
        }
    
    print("=" * width)
    print("EVENING DEBRIEF".center(width))
    print("=" * width)
    print("TODAYS LOG:")
     
    return answers


def save_journal(activity, journal_input):
    
    today_date = datetime.now().date()
    today = today_date.strftime("%Y-%m-%d")
    yesterday = (today_date - timedelta(days=1)).strftime("%Y-%m-%d")
    file_name = f"{today}.md"
    file_path = Path(OBSIDIAN_PATH) / file_name
    total_commits = sum(data["commits"] for data in activity.values())
    table_rows = ""

    # build rows without those days with no repos
    for date, data in activity.items():
        if data["repos"]:
            repos_str = ", ".join(r.split("/")[1] for r in data["repos"]) if data["repos"] else "no repos"
            table_rows += f"| {date} | {data["commits"]} | {repos_str} |\n"

    content = f""" 
    # Dev Log - {today}

    ## GitHub Activity
    | Date | Commits | Repos |
    |------|---------|-------|
    {table_rows}

    ** Total this week: {total_commits} commits**

    ## Evening Debrief

    **worked on:** {journal_input["worked_on"]}

    **Learned:** {journal_input["learned"]}

    **Tomorrow:** {journal_input["tomorrow"]}

    **Blockers:** {journal_input["blockers"]} 
    """

    # Write content into Obsidian
    with open(file_path, "w" , encoding="utf-8") as f:
        f.write(content)

    print(f"Journal saved to {file_path}")



activity = get_github_activity()
display_activity(activity)
journal_input = get_journal_input()
save_journal(activity, journal_input)