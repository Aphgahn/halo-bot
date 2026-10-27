import os
import json
import base64
import urllib.request
import urllib.error
import asyncio


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "Aphgahn/halo-bot")
GITHUB_FILE = os.getenv("GITHUB_FILE", "roster.json")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")


DEFAULT_ROSTER = {
    "captain": None,
    "co_captain": None,
    "players": [],
    "additional_rosters": [],
    "roster_name": "HALO",
    "looking_at_name": "Tryouts",
    "looking_at": [],
    "roster_channel": None,
    "roster_message": None
}


def github_url():
    return f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"


def github_request(method, url, data=None):
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN environment variable is not set.")

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "halo-discord-bot"
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub API error {e.code}: {error_body}")


async def get_roster():
    def _get():
        try:
            response = github_request("GET", github_url())
            content = base64.b64decode(response["content"]).decode("utf-8")
            data = json.loads(content)
            for key, value in DEFAULT_ROSTER.items():
                if key not in data:
                    data[key] = value.copy() if isinstance(value, (list, dict)) else value
            if not isinstance(data.get("additional_rosters"), list):
                data["additional_rosters"] = []
            for roster in data["additional_rosters"]:
                roster.setdefault("name", "Additional Roster")
                roster.setdefault("players", [])
                roster.setdefault("captain", None)
                roster.setdefault("co_captain", None)
            # Move the old global tryouts list into a normal roster exactly once.
            if not data.get("_tryouts_migrated"):
                tryout_players = data.get("looking_at", [])
                tryout_name = data.get("looking_at_name", "Tryouts")
                if tryout_players or tryout_name != "Tryouts":
                    data["additional_rosters"].append({"name": tryout_name or "Tryouts", "players": list(tryout_players)})
                data["looking_at"] = []
                data["looking_at_name"] = "Tryouts"
                data["_tryouts_migrated"] = True
            return data
        except RuntimeError as e:
            print(f"[GitHub] Failed to load roster: {e}")
            return {**DEFAULT_ROSTER, "players": [], "looking_at": [], "additional_rosters": []}
    return await asyncio.to_thread(_get)


async def save_roster(data, commit_message="Update roster"):
    def _save():
        response = github_request("GET", github_url())
        sha = response["sha"]
        formatted_json = json.dumps(data, indent=4) + "\n"
        encoded = base64.b64encode(formatted_json.encode("utf-8")).decode("utf-8")
        payload = {
            "message": commit_message,
            "content": encoded,
            "sha": sha,
            "branch": GITHUB_BRANCH
        }
        github_request("PUT", github_url(), payload)
        print(f"[GitHub] Saved roster: {commit_message}")
    await asyncio.to_thread(_save)
