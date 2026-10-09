#!/usr/bin/env python3
"""Fetches public GitHub stats into stats.json (uses GITHUB_TOKEN if set).

Projects counted per language = your own non-fork repos, plus repos you
contributed to (last 12 months, public, needs a token) unless
CONFIG["include_contributions"] is false."""
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from build_readme import CONFIG

user = CONFIG["github_user"]
if user.startswith("YOUR-"):
    sys.exit("set github_user to your real GitHub username.")
TOKEN = os.getenv("GITHUB_TOKEN")

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    return json.load(urllib.request.urlopen(req))

GQL = """
fragment R on Repository {
  nameWithOwner isArchived isPrivate owner { login }
  languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
}
query($login: String!) {
  user(login: $login) { contributionsCollection {
    commitContributionsByRepository(maxRepositories: 100) { repository { ...R } }
    pullRequestContributionsByRepository(maxRepositories: 100) { repository { ...R } }
  } }
}"""

def contributed_projects():
    """Repos owned by others that you committed to or opened PRs in (public only)."""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": GQL, "variables": {"login": user}}).encode(),
        headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req))
    if data.get("errors"):
        raise RuntimeError(data["errors"][0].get("message", "GraphQL error"))
    coll = data["data"]["user"]["contributionsCollection"]
    found = {}
    for key in ("commitContributionsByRepository", "pullRequestContributionsByRepository"):
        for item in coll[key]:
            r = item["repository"]
            if r["isPrivate"] or r["isArchived"] or r["owner"]["login"].lower() == user.lower():
                continue
            found[r["nameWithOwner"]] = {e["node"]["name"]: e["size"] for e in r["languages"]["edges"]}
    return found

COMMITS_GQL = """
query($login: String!, $yearStart: DateTime!, $dayStart: DateTime!, $now: DateTime!) {
  year: user(login: $login) { contributionsCollection(from: $yearStart, to: $now) { totalCommitContributions } }
  day:  user(login: $login) { contributionsCollection(from: $dayStart, to: $now) { totalCommitContributions } }
}"""

def commit_counts():
    """(commits this calendar year, commits today) in CONFIG["timezone"] (default UTC).
    Public commits to default branches, as GitHub counts them on your profile."""
    tz = ZoneInfo(CONFIG.get("timezone", "UTC"))
    now = datetime.now(tz)
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    iso = lambda d: d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": COMMITS_GQL, "variables": {
            "login": user, "yearStart": iso(year_start),
            "dayStart": iso(day_start), "now": iso(now)}}).encode(),
        headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req))
    if data.get("errors"):
        raise RuntimeError(data["errors"][0].get("message", "GraphQL error"))
    d = data["data"]
    return (d["year"]["contributionsCollection"]["totalCommitContributions"],
            d["day"]["contributionsCollection"]["totalCommitContributions"])

try:
    u = get(f"https://api.github.com/users/{user}")
    repos = get(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner")
except urllib.error.HTTPError as err:
    if err.code == 404:
        sys.exit(f"GitHub says user '{user}' doesn't exist. Check github_user.")
    print(f"GitHub API error {err.code} ({err.reason}); keeping the existing stats.json.")
    sys.exit(0)

projects = {}   # name -> {language: bytes}
for r in repos:
    if r["fork"] or r["archived"]:
        continue
    try:
        projects[r["full_name"]] = get(r["languages_url"])
    except urllib.error.HTTPError:
        projects[r["full_name"]] = {r["language"]: 1} if r["language"] else {}

contributed = {}
if CONFIG.get("include_contributions", True):
    if not TOKEN:
        print("No GITHUB_TOKEN set: skipping repos you contributed to.")
    else:
        try:
            contributed = contributed_projects()
        except Exception as err:   # never break the build over this
            print(f"Couldn't fetch contributions ({err}); using your own repos only.")
projects.update(contributed)

# Count projects (not code size): a project counts for every language that
# makes up at least 5% of its bytes, so Unity/shader boilerplate stays out.
langs = {}
for by_bytes in projects.values():
    total = sum(by_bytes.values()) or 1
    for l, n in by_bytes.items():
        if n / total >= 0.05:
            langs[l] = langs.get(l, 0) + 1

prior = json.load(open("stats.json")) if os.path.exists("stats.json") else {}
commits_year, commits_today = prior.get("commits_year", 0), prior.get("commits_today", 0)
if not TOKEN:
    print("No GITHUB_TOKEN set: keeping the previous commit counts.")
else:
    try:
        commits_year, commits_today = commit_counts()
    except Exception as err:   # never break the build over this
        print(f"Couldn't fetch commit counts ({err}); keeping the previous ones.")

json.dump({"repos": u["public_repos"], "followers": u["followers"],
           "stars": sum(r["stargazers_count"] for r in repos),
           "contributed": len(contributed),
           "commits_year": commits_year, "commits_today": commits_today,
           "languages": langs}, open("stats.json", "w"), indent=2)
print(f"stats.json updated ({len(projects)} projects, {len(contributed)} contributed to, "
      f"{commits_year} commits this year, {commits_today} today)")