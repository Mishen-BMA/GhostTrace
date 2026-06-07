import requests
import threading
from ghosttrace.modules.colors import field, section, info, GREEN, GRAY, WHITE, RESET

PLATFORMS = [
    ("GitHub",       "https://github.com/{u}",                       "status", 200),
    ("GitLab",       "https://gitlab.com/{u}",                       "status", 200),
    ("Twitter/X",    "https://x.com/{u}",                            "status", 200),
    ("Reddit",       "https://www.reddit.com/user/{u}",              "status", 200),
    ("Instagram",    "https://www.instagram.com/{u}/",               "status", 200),
    ("TikTok",       "https://www.tiktok.com/@{u}",                  "status", 200),
    ("YouTube",      "https://www.youtube.com/@{u}",                 "status", 200),
    ("Pinterest",    "https://www.pinterest.com/{u}/",               "status", 200),
    ("Tumblr",       "https://{u}.tumblr.com",                       "status", 200),
    ("Medium",       "https://medium.com/@{u}",                      "status", 200),
    ("Dev.to",       "https://dev.to/{u}",                           "status", 200),
    ("Hashnode",     "https://hashnode.com/@{u}",                    "status", 200),
    ("Twitch",       "https://www.twitch.tv/{u}",                    "status", 200),
    ("Steam",        "https://steamcommunity.com/id/{u}",            "status", 200),
    ("Keybase",      "https://keybase.io/{u}",                       "status", 200),
    ("HackerNews",   "https://news.ycombinator.com/user?id={u}",     "text",   "user?id="),
    ("Product Hunt", "https://www.producthunt.com/@{u}",             "status", 200),
    ("Pastebin",     "https://pastebin.com/u/{u}",                   "status", 200),
    ("DockerHub",    "https://hub.docker.com/u/{u}",                 "status", 200),
    ("NPM",          "https://www.npmjs.com/~{u}",                   "status", 200),
    ("PyPI",         "https://pypi.org/user/{u}/",                   "status", 200),
    ("HackTheBox",   "https://app.hackthebox.com/users/profile/{u}", "status", 200),
    ("TryHackMe",    "https://tryhackme.com/p/{u}",                  "status", 200),
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def _check(username, name, url_tpl, check_type, match, found, lock):
    url = url_tpl.replace("{u}", username)
    try:
        r = requests.get(url, headers=HEADERS, timeout=6, allow_redirects=True)
        hit = (check_type == "status" and r.status_code == match) or \
              (check_type == "text"   and match in r.text)
        if hit:
            with lock:
                found[name] = url
    except Exception:
        pass

def scan_username(username: str) -> dict:
    results = {"target": username, "type": "username"}
    section(f"USERNAME HUNT  —  @{username}")
    print(f"  {GRAY}Scanning {len(PLATFORMS)} platforms, please wait...{RESET}\n")

    found = {}
    lock  = threading.Lock()
    threads = [
        threading.Thread(target=_check, args=(username, name, url_tpl, ct, match, found, lock))
        for name, url_tpl, ct, match in PLATFORMS
    ]
    for t in threads: t.start()
    for t in threads: t.join()

    section(f"RESULTS  —  {len(found)} of {len(PLATFORMS)} platforms matched")
    all_checked = []
    for name, url_tpl, _, _ in PLATFORMS:
        if name in found:
            print(f"  {GREEN}[FOUND]{RESET}  {name:<18} {WHITE}{found[name]}{RESET}")
            all_checked.append({"platform": name, "url": found[name], "found": True})
        else:
            print(f"  {GRAY}[-----]{RESET}  {name:<18} not found")
            all_checked.append({"platform": name, "found": False})

    results["platforms"]   = all_checked
    results["found_count"] = len(found)
    return results