#!/usr/bin/env python3
"""Fetches public GitHub stats into stats.json (uses GITHUB_TOKEN if set)."""
import json, os, urllib.request
from build_readme import CONFIG

user = CONFIG["github_user"]
def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if os.getenv("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    return json.load(urllib.request.urlopen(req))

u = get(f"https://api.github.com/users/{user}")
repos = get(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner")
langs = {}
for r in repos:
    if not r["fork"] and r["language"]:
        langs[r["language"]] = langs.get(r["language"], 0) + max(r["size"], 1)
events = get(f"https://api.github.com/users/{user}/events/public?per_page=100")
commits = sum(len(e["payload"].get("commits", [])) for e in events if e["type"] == "PushEvent")
json.dump({"repos": u["public_repos"], "followers": u["followers"],
           "stars": sum(r["stargazers_count"] for r in repos),
           "commits": commits, "languages": langs}, open("stats.json", "w"), indent=2)
