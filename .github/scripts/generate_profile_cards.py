import os
import json
import pathlib
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path("assets")
ROOT.mkdir(exist_ok=True)

USERNAME = os.environ.get("USERNAME", "")
TOKEN = os.environ.get("GH_TOKEN", "")

def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

def write(path, text):
    path.write_text(text, encoding="utf-8")

def api_get(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-cards-workflow",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)

def card_shell(title, subtitle, body, width=1200, height=420):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
  <rect width="100%" height="100%" rx="28" fill="#ffffff" stroke="#e2e8f0" />
  <text x="36" y="64" font-size="34" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">{esc(title)}</text>
  <text x="36" y="96" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">{esc(subtitle)}</text>
  {body}
</svg>"""

def write_fallback(reason):
    stats_body = """
  <rect x="40" y="132" width="320" height="220" rx="24" fill="#f8fafc" stroke="#e2e8f0" />
  <rect x="440" y="132" width="320" height="220" rx="24" fill="#f8fafc" stroke="#e2e8f0" />
  <rect x="840" y="132" width="320" height="220" rx="24" fill="#f8fafc" stroke="#e2e8f0" />
  <text x="200" y="210" text-anchor="middle" font-size="20" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Public Repos</text>
  <text x="600" y="210" text-anchor="middle" font-size="20" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Followers</text>
  <text x="1000" y="210" text-anchor="middle" font-size="20" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Following</text>
  <text x="200" y="285" text-anchor="middle" font-size="56" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">--</text>
  <text x="600" y="285" text-anchor="middle" font-size="56" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">--</text>
  <text x="1000" y="285" text-anchor="middle" font-size="56" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">--</text>
  <text x="36" y="390" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Fallback card generated because live data was unavailable.</text>
"""
    activity_body = """
  <rect x="64" y="126" width="1072" height="220" rx="20" fill="#f8fafc" stroke="#e2e8f0" />
  <polyline points="90,310 180,260 270,285 360,205 450,235 540,180 630,230 720,150 810,220 900,175 990,205 1080,140" fill="none" stroke="#10b981" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <polygon points="90,310 180,260 270,285 360,205 450,235 540,180 630,230 720,150 810,220 900,175 990,205 1080,140 1080,346 90,346" fill="#d1fae5"/>
  <text x="36" y="390" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Fallback graph generated because live event data was unavailable.</text>
"""
    ach_body = f"""
  <rect x="40" y="126" width="1120" height="48" rx="18" fill="#f8fafc" stroke="#e2e8f0" />
  <rect x="40" y="188" width="1120" height="48" rx="18" fill="#f8fafc" stroke="#e2e8f0" />
  <rect x="40" y="250" width="1120" height="48" rx="18" fill="#f8fafc" stroke="#e2e8f0" />
  <text x="80" y="156" font-size="20" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">Workflow Ready</text>
  <text x="80" y="218" font-size="20" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">Stable Local Assets</text>
  <text x="80" y="280" font-size="20" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">No Broken External Widgets</text>
  <text x="36" y="390" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">{esc(reason)}</text>
"""
    write(ROOT / "github-stats.svg", card_shell("GitHub Stats", f"Auto-generated for @{USERNAME or 'your-profile'}", stats_body))
    write(ROOT / "activity-graph.svg", card_shell("Activity Graph", "Recent public activity overview", activity_body))
    write(ROOT / "achievements.svg", card_shell("Achievements", "Profile milestones and workflow status", ach_body))

def main():
    if not USERNAME:
        write_fallback("USERNAME was not provided.")
        return

    try:
        profile = api_get(f"https://api.github.com/users/{USERNAME}")
        events = api_get(f"https://api.github.com/users/{USERNAME}/events/public?per_page=100")

        public_repos = int(profile.get("public_repos", 0))
        followers = int(profile.get("followers", 0))
        following = int(profile.get("following", 0))
        event_count = len(events) if isinstance(events, list) else 0

        stats_body = f"""
  <rect x="40" y="132" width="320" height="220" rx="24" fill="#f8fafc" stroke="#e2e8f0" />
  <rect x="440" y="132" width="320" height="220" rx="24" fill="#f8fafc" stroke="#e2e8f0" />
  <rect x="840" y="132" width="320" height="220" rx="24" fill="#f8fafc" stroke="#e2e8f0" />
  <circle cx="78" cy="170" r="10" fill="#3b82f6" />
  <circle cx="478" cy="170" r="10" fill="#6366f1" />
  <circle cx="878" cy="170" r="10" fill="#f59e0b" />
  <text x="100" y="176" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Public Repositories</text>
  <text x="500" y="176" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Followers</text>
  <text x="900" y="176" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Following</text>
  <text x="200" y="260" text-anchor="middle" font-size="64" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">{public_repos}</text>
  <text x="600" y="260" text-anchor="middle" font-size="64" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">{followers}</text>
  <text x="1000" y="260" text-anchor="middle" font-size="64" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">{following}</text>
  <text x="200" y="316" text-anchor="middle" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Visible on your public profile</text>
  <text x="600" y="316" text-anchor="middle" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">GitHub profile followers</text>
  <text x="1000" y="316" text-anchor="middle" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Accounts you follow</text>
"""
        write(ROOT / "github-stats.svg", card_shell("GitHub Stats", f"Auto-generated for @{USERNAME}", stats_body))

        today = datetime.now(timezone.utc).date()
        start = today - timedelta(days=27)
        counts = {start + timedelta(days=i): 0 for i in range(28)}
        for event in events if isinstance(events, list) else []:
            created = event.get("created_at")
            if not created:
                continue
            try:
                day = datetime.fromisoformat(created.replace("Z", "+00:00")).date()
            except ValueError:
                continue
            if day in counts:
                counts[day] += 1

        ordered = list(counts.items())
        max_count = max((v for _, v in ordered), default=1)
        max_count = max(max_count, 1)
        plot_x, plot_y, plot_w, plot_h = 64, 126, 1072, 220
        spacing = plot_w / max(len(ordered) - 1, 1)
        pts = []
        labels = []
        for idx, (day, val) in enumerate(ordered):
            x = plot_x + idx * spacing
            y = plot_y + plot_h - (val / max_count) * (plot_h - 24)
            pts.append((x, y))
            labels.append(day.strftime("%m-%d"))
        points = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        area_points = f"{plot_x},{plot_y + plot_h} " + " ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + f" {plot_x + plot_w},{plot_y + plot_h}"
        grid = []
        for i in range(5):
            gy = plot_y + i * (plot_h / 4)
            grid.append(f'<line x1="{plot_x}" y1="{gy:.2f}" x2="{plot_x + plot_w}" y2="{gy:.2f}" stroke="#e2e8f0" />')
        tick_marks = []
        for idx in range(0, len(labels), 4):
            x = plot_x + idx * spacing
            tick_marks.append(f'<text x="{x:.2f}" y="372" text-anchor="middle" font-size="14" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">{labels[idx]}</text>')
        activity_body = f"""
  <rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" rx="20" fill="#f8fafc" stroke="#e2e8f0" />
  {''.join(grid)}
  <polygon points="{area_points}" fill="#d1fae5" />
  <polyline points="{points}" fill="none" stroke="#10b981" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
  {''.join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#10b981" />' for x, y in pts)}
  {''.join(tick_marks)}
  <text x="36" y="390" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Recent 28 days based on public events API · total recent events: {event_count}</text>
"""
        write(ROOT / "activity-graph.svg", card_shell("Activity Graph", "Recent public activity overview", activity_body))

        achievements = [
            ("Open Portfolio", public_repos >= 1, "Has at least one public repository."),
            ("Growing Presence", followers >= 1, "Has at least one GitHub follower."),
            ("Active Profile", event_count >= 5, "Has several recent public GitHub events."),
            ("Connected Builder", following >= 1, "Actively follows other GitHub accounts."),
        ]
        rows = []
        y_base = 126
        for idx, (name, unlocked, desc) in enumerate(achievements):
            fill = "#eef2ff" if unlocked else "#f8fafc"
            dot = "#6366f1" if unlocked else "#cbd5e1"
            state = "Unlocked" if unlocked else "In Progress"
            yy = y_base + idx * 62
            rows.append(f"""
  <rect x="40" y="{yy}" width="1120" height="48" rx="18" fill="{fill}" stroke="#e2e8f0" />
  <circle cx="70" cy="{yy + 24}" r="9" fill="{dot}" />
  <text x="96" y="{yy + 20}" font-size="20" font-weight="700" fill="#0f172a" font-family="Inter,Segoe UI,Arial,sans-serif">{esc(name)}</text>
  <text x="96" y="{yy + 38}" font-size="15" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">{esc(desc)}</text>
  <text x="1110" y="{yy + 30}" text-anchor="end" font-size="16" fill="#475569" font-family="Inter,Segoe UI,Arial,sans-serif">{state}</text>
""")
        ach_body = "".join(rows) + f'<text x="36" y="390" font-size="18" fill="#64748b" font-family="Inter,Segoe UI,Arial,sans-serif">Generated from live GitHub profile data for @{esc(USERNAME)}.</text>'
        write(ROOT / "achievements.svg", card_shell("Achievements", "Profile milestones based on current GitHub data", ach_body))

    except Exception as exc:
        write_fallback(f"Fallback mode: {type(exc).__name__} while loading live data.")

if __name__ == "__main__":
    main()
