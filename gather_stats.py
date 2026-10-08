#!/usr/bin/env python3
"""Fetches public GitHub stats into stats.json (uses GITHUB_TOKEN if set)."""
import json, os, sys, urllib.request, urllib.error
from build_readme import CONFIG

user = CONFIG["github_user"]
if user.startswith("YOUR-"):
    sys.exit("config.json: set github_user to your real GitHub username.")

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if os.getenv("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    return json.load(urllib.request.urlopen(req))

try:
    u = get(f"https://api.github.com/users/{user}")
    repos = get(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner")
    events = get(f"https://api.github.com/users/{user}/events/public?per_page=100")
except urllib.error.HTTPError as err:
    if err.code == 404:
        sys.exit(f"GitHub says user '{user}' doesn't exist. Check github_user in config.json.")
    print(f"GitHub API error {err.code} ({err.reason}); keeping the existing stats.json.")
    sys.exit(0)


langs = {}
for r in repos:
    if r["fork"] or r["archived"]:
        continue
    try:
        by_bytes = get(r["languages_url"])
        total = sum(by_bytes.values()) or 1
        used = [l for l, n in by_bytes.items() if n / total >= 0.05]
    except urllib.error.HTTPError:
        used = [r["language"]] if r["language"] else []
    for l in used:
        langs[l] = langs.get(l, 0) + 1
commits = sum(len(ev["payload"].get("commits", [])) for ev in events if ev["type"] == "PushEvent")
json.dump({"repos": u["public_repos"], "followers": u["followers"],
           "stars": sum(r["stargazers_count"] for r in repos),
           "commits": commits, "languages": langs}, open("stats.json", "w"), indent=2)
print("stats.json updated")