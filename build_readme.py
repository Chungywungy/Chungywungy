#!/usr/bin/env python3
"""Builds the profile README: themed SVGs (light + dark) and README.md.
Edit CONFIG, run `python build_readme.py`, commit the output."""
import json, os
from html import escape

CONFIG = {
    "handle": "Chungywungy",
    "github_user": "Chungywungy",   # <- change me
    "tagline": "I make things",
    "about": [   # (key, value) rows for the profile panel
        ("Languages",  "Python, Java, Javascript, C, Typescript"),
        ("",   "blender, c#, python, git"),
        ("themes",  "horror aesthetics + technical modding"),
        ("status",  "open to collabs and mod ideas"),
    ],
    "now": [     # (marker, text) — marker: ">" active, "~" paused, "+" shipped
        (">", "BCIT: Computer Systems Technology"),
        (">", ""),
        ("~", "add another project here"),
    ],
    "stack": {   # group -> tags
        "art":     ["blender", "substance painter", "photoshop"],
        "modding": ["unity", "c#", "bepinex"],
        "code":    ["python", "java", "git"],
    },
    "reach": [   # (label, url)
        ("github",  "https://github.com/Chungywungy"),
        ("email",   "mailto:fshariff3@my.bcit.ca"),
        ("website", ""),
        ("discord", ""),
    ],
}

W = 840
FONT = "'SFMono-Regular','Cascadia Mono',Consolas,'Courier New',monospace"
PAL = {
  "dark":  dict(bg="#0D0F0C", panel="#131611", line="#2A2F24", text="#D9DCCB",
                dim="#7C846B", accent="#A3B34C", alert="#C4452D", ghost="#3E4A1E"),
  "light": dict(bg="#ECEEE6", panel="#F6F7F1", line="#C9CDBB", text="#1C2016",
                dim="#66705A", accent="#5F6E1F", alert="#B03A24", ghost="#B9C48A"),
}
e = escape

def svg(w, h, body, p, bg=None):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="{FONT}">'
            f'<rect width="{w}" height="{h}" rx="8" fill="{bg or p["panel"]}" '
            f'stroke="{p["line"]}"/>{body}</svg>')

def hero(c, p):
    h = 230
    name, tag = e(c["handle"]), e(c["tagline"])
    scan = "".join(f'<rect y="{y}" width="{W}" height="1" fill="{p["line"]}" opacity=".35"/>'
                   for y in range(6, h, 6))
    body = f'''{scan}
<text x="46" y="58" font-size="13" fill="{p["dim"]}">cam 01</text>
<circle cx="{W-118}" cy="53" r="5" fill="{p["alert"]}"><animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.5;.5;.9;1" dur="1.6s" repeatCount="indefinite"/></circle>
<text x="{W-106}" y="58" font-size="13" fill="{p["alert"]}">rec</text>
<text x="40" y="146" font-size="76" font-weight="700" fill="{p["alert"]}" opacity=".55">{name}</text>
<text x="52" y="142" font-size="76" font-weight="700" fill="{p["ghost"]}">{name}</text>
<text x="46" y="144" font-size="76" font-weight="700" fill="{p["accent"]}">{name}</text>
<text x="48" y="190" font-size="17" fill="{p["text"]}">{tag}</text>'''
    return svg(W, h, body, p, p["bg"])

def bar(title, p):
    body = (f'<rect x="14" y="13" width="10" height="10" fill="{p["accent"]}"/>'
            f'<text x="36" y="23" font-size="15" font-weight="700" fill="{p["text"]}">{e(title)}</text>'
            f'<rect x="{40+len(title)*9}" y="18" width="{W-60-len(title)*9}" height="1" fill="{p["line"]}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="36" viewBox="0 0 {W} 36" font-family="{FONT}">{body}</svg>'

def profile(c, p):
    rows = c["about"]; h = 70 + 30 * len(rows)
    out = f'<text x="28" y="40" font-size="15" fill="{p["accent"]}">{e(c["handle"])}@workshop</text>'
    out += f'<rect x="28" y="52" width="{W-56}" height="1" fill="{p["line"]}"/>'
    for i, (k, v) in enumerate(rows):
        y = 84 + 30 * i
        out += (f'<text x="28" y="{y}" font-size="14" fill="{p["dim"]}">{e(k)}</text>'
                f'<text x="140" y="{y}" font-size="14" fill="{p["text"]}">{e(v)}</text>')
    return svg(W, h, out, p)

def now(c, p):
    rows = c["now"]; h = 30 + 36 * len(rows)
    col = {">": p["accent"], "~": p["dim"], "+": p["text"]}
    out = ""
    for i, (m, t) in enumerate(rows):
        y = 44 + 36 * i
        out += (f'<text x="28" y="{y}" font-size="15" font-weight="700" fill="{col.get(m, p["dim"])}">{e(m)}</text>'
                f'<text x="52" y="{y}" font-size="14" fill="{p["text"]}">{e(t)}</text>')
    return svg(W, h, out, p)

def stack(c, p):
    groups = c["stack"]; h = 30 + 46 * len(groups); out = ""
    for i, (g, tags) in enumerate(groups.items()):
        y = 44 + 46 * i
        out += f'<text x="28" y="{y}" font-size="14" fill="{p["dim"]}">{e(g)}</text>'
        x = 140
        for t in tags:
            tw = int(len(t) * 8.4 + 22)
            out += (f'<rect x="{x}" y="{y-19}" width="{tw}" height="28" rx="4" fill="{p["bg"]}" stroke="{p["line"]}"/>'
                    f'<text x="{x+11}" y="{y}" font-size="13" fill="{p["text"]}">{e(t)}</text>')
            x += tw + 10
    return svg(W, h, out, p)

def activity(stats, p):
    h = 200; out = ""
    items = [("repos", stats.get("repos", 0)), ("stars", stats.get("stars", 0)),
             ("followers", stats.get("followers", 0)), ("recent commits", stats.get("commits", 0))]
    for i, (k, v) in enumerate(items):
        x = 28 + i * 200
        out += (f'<text x="{x}" y="58" font-size="34" font-weight="700" fill="{p["accent"]}">{v}</text>'
                f'<text x="{x}" y="80" font-size="13" fill="{p["dim"]}">{e(k)}</text>')
    langs = stats.get("languages", {})   # language -> number of projects using it
    total = sum(langs.values()) or 1
    out += f'<text x="28" y="122" font-size="13" fill="{p["dim"]}">projects by language</text>'
    shades = [p["accent"], p["alert"], p["text"], p["dim"], p["ghost"]]
    x, bw, lx = 28, W - 56, 28
    for i, (name, n) in enumerate(sorted(langs.items(), key=lambda kv: -kv[1])[:5]):
        w = max(4, bw * n / total)
        out += f'<rect x="{x:.1f}" y="134" width="{w:.1f}" height="10" fill="{shades[i]}"/>'
        label = f"{name} {n}"
        out += (f'<rect x="{lx}" y="164" width="10" height="10" fill="{shades[i]}"/>'
                f'<text x="{lx+16}" y="173" font-size="12" fill="{p["text"]}">{e(label)}</text>')
        lx += int(len(label) * 7.4 + 44)
        x += w
    return svg(W, h, out, p)

def button(label, p):
    w = int(len(label) * 9 + 44)
    body = (f'<rect x=".5" y=".5" width="{w-1}" height="39" rx="6" fill="{p["panel"]}" stroke="{p["accent"]}"/>'
            f'<text x="{w/2}" y="25" font-size="14" text-anchor="middle" fill="{p["text"]}">{e(label)}</text>')
    return w, f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="40" viewBox="0 0 {w} 40" font-family="{FONT}">{body}</svg>'

def pic(name, alt):
    base = "assets/" + name
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="{base}-dark.svg">\n'
            f'  <img alt="{alt}" src="{base}-light.svg">\n</picture>')

def main():
    c = CONFIG
    os.makedirs("assets", exist_ok=True)
    stats = json.load(open("stats.json")) if os.path.exists("stats.json") else {}
    for mode, p in PAL.items():
        files = {"hero": hero(c, p), "profile": profile(c, p), "now": now(c, p),
                 "stack": stack(c, p), "activity": activity(stats, p)}
        for t in ("about", "now", "stack", "activity", "reach"):
            files["bar-" + t] = bar(t, p)
        for label, _ in c["reach"]:
            files["btn-" + label] = button(label, p)[1]
        for n, s in files.items():
            open(f"assets/{n}-{mode}.svg", "w").write(s)
    parts = [pic("hero", c["handle"])]
    for bar_n, panel_n in (("about", "profile"), ("now", "now"), ("stack", "stack"), ("activity", "activity")):
        parts.append(pic("bar-" + bar_n, bar_n) + "\n" + pic(panel_n, panel_n))
    btns = "".join(f'<a href="{u}">' + pic("btn-" + l, l).replace("\n", "") + "</a>" for l, u in c["reach"])
    parts.append(pic("bar-reach", "reach") + "\n" + btns)
    open("README.md", "w").write("\n\n".join(parts) + "\n")

if __name__ == "__main__":
    main()
