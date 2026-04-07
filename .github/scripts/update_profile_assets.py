\
from __future__ import annotations

import json
import os
import pathlib
import shutil
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

ROOT = pathlib.Path(".")
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
hour = now.hour

TIME_CONFIG = {
    "morning": {
        "range": lambda h: 5 <= h < 11,
        "message": "좋은 아침입니다. 오늘도 좋은 하루 되세요.",
        "color": "#FACC15",
        "label": "MORNING",
        "stickers": "🌞 🌼 ☀️",
    },
    "afternoon": {
        "range": lambda h: 11 <= h < 17,
        "message": "점심 인사드립니다. 절반, 거의 다 왔네요. 힘내세요!",
        "color": "#38BDF8",
        "label": "AFTERNOON",
        "stickers": "☁️ 🩵 🌤️",
    },
    "evening": {
        "range": lambda h: 17 <= h < 22,
        "message": "석양이 지고있네요. 오늘 하루도 고생 많으셨습니다.",
        "color": "#F97316",
        "label": "EVENING",
        "stickers": "🌇 🍂 🕯️",
    },
    "night": {
        "range": lambda h: h >= 22 or h < 5,
        "message": "좋은 새벽입니다. 조용한 시간 속에서도 당신의 하루를 응원합니다.",
        "color": "#111827",
        "label": "DAWN",
        "stickers": "🌙 ✨ 🌌",
    },
}

slot = next(name for name, cfg in TIME_CONFIG.items() if cfg["range"](hour))
cfg = TIME_CONFIG[slot]

def write_text(path: pathlib.Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")

def request_json(url: str):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "github-profile-readme-updater"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)

def card_shell(title: str, subtitle: str, body: str, width: int = 1200, height: int = 420) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
  <defs>
    <linearGradient id="soft" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="100%" stop-color="#f8fafc" />
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" rx="28" fill="url(#soft)" stroke="#e2e8f0" />
  <text x="36" y="64" font-size="34" font-weight="700" fill="#0f172a" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">{escape(title)}</text>
  <text x="36" y="96" font-size="18" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">{escape(subtitle)}</text>
  {body}
</svg>"""

def make_greeting() -> None:
    color = cfg["color"]
    if slot == "night":
        bg = "#F3F4F6"
        text = "#111827"
        sub = "#374151"
    elif slot == "morning":
        bg = "#FFFDF5"
        text = color
        sub = "#475569"
    elif slot == "afternoon":
        bg = "#F0F9FF"
        text = color
        sub = "#475569"
    else:
        bg = "#FFF7ED"
        text = color
        sub = "#475569"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="190" viewBox="0 0 1200 190" role="img" aria-label="time based greeting">
  <rect width="100%" height="100%" rx="28" fill="{bg}" stroke="#e2e8f0" />
  <text x="50%" y="62" text-anchor="middle" font-size="24" font-weight="700" fill="{text}" font-family="Georgia, Times New Roman, Apple SD Gothic Neo, Malgun Gothic, serif">{escape(cfg["stickers"])}  {escape(cfg["label"])}  {escape(cfg["stickers"])}</text>
  <text x="50%" y="118" text-anchor="middle" font-size="34" font-weight="800" fill="{text}" font-family="Georgia, Times New Roman, Apple SD Gothic Neo, Malgun Gothic, serif">{escape(cfg["message"])}</text>
  <text x="50%" y="154" text-anchor="middle" font-size="16" fill="{sub}" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">Asia/Seoul · updated automatically by GitHub Actions</text>
</svg>"""
    write_text(ASSETS / "greeting.svg", svg)

def select_banner() -> None:
    dest = ROOT / "current-banner.png"
    candidates = [
        ROOT / f"{slot}.png",
        ROOT / "banner.png",
        dest,
    ]
    source = next((p for p in candidates if p.exists()), None)
    if source and source.resolve() != dest.resolve():
        shutil.copyfile(source, dest)

def safe_profile(username: str):
    try:
        profile = request_json(f"https://api.github.com/users/{username}")
    except Exception:
        profile = {"public_repos": 0, "followers": 0, "following": 0}
    try:
        events = request_json(f"https://api.github.com/users/{username}/events/public?per_page=100")
        if not isinstance(events, list):
            events = []
    except Exception:
        events = []
    return profile, events

def build_stats(profile: dict) -> None:
    repos = int(profile.get("public_repos", 0) or 0)
    followers = int(profile.get("followers", 0) or 0)
    following = int(profile.get("following", 0) or 0)

    body = f"""
  <rect x="40" y="132" width="320" height="220" rx="24" fill="#f8fafc" stroke="#e2e8f0" />
  <rect x="440" y="132" width="320" height="220" rx="24" fill="#f8fafc" stroke="#e2e8f0" />
  <rect x="840" y="132" width="320" height="220" rx="24" fill="#f8fafc" stroke="#e2e8f0" />

  <circle cx="78" cy="170" r="10" fill="#3b82f6" />
  <circle cx="478" cy="170" r="10" fill="#6366f1" />
  <circle cx="878" cy="170" r="10" fill="#f59e0b" />

  <text x="100" y="176" font-size="18" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">Public Repositories</text>
  <text x="500" y="176" font-size="18" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">Followers</text>
  <text x="900" y="176" font-size="18" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">Following</text>

  <text x="200" y="260" text-anchor="middle" font-size="64" font-weight="700" fill="#0f172a" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">{repos}</text>
  <text x="600" y="260" text-anchor="middle" font-size="64" font-weight="700" fill="#0f172a" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">{followers}</text>
  <text x="1000" y="260" text-anchor="middle" font-size="64" font-weight="700" fill="#0f172a" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">{following}</text>

  <text x="200" y="316" text-anchor="middle" font-size="18" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">Visible on your GitHub profile</text>
  <text x="600" y="316" text-anchor="middle" font-size="18" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">Current public follower count</text>
  <text x="1000" y="316" text-anchor="middle" font-size="18" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">Accounts you follow</text>
"""
    write_text(ASSETS / "github-stats.svg", card_shell("GitHub Stats", "Live values from the public GitHub profile API", body))

def build_graph(events: list[dict]) -> tuple[int, int]:
    counts = Counter()
    today = now.date()

    for ev in events:
        ts = ev.get("created_at")
        if not ts:
            continue
        try:
            d = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(KST).date()
        except Exception:
            continue
        if 0 <= (today - d).days < 28:
            counts[d.isoformat()] += 1

    dates = [(today - timedelta(days=27 - i)) for i in range(28)]
    values = [counts.get(d.isoformat(), 0) for d in dates]
    max_v = max(max(values), 1)

    plot_x, plot_y, plot_w, plot_h = 64, 126, 1072, 220
    step = plot_w / max(len(values) - 1, 1)
    pts = []
    for i, v in enumerate(values):
        x = plot_x + i * step
        y = plot_y + plot_h - (v / max_v) * (plot_h - 24)
        pts.append((x, y))

    points = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    area = f"{plot_x},{plot_y + plot_h} " + " ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + f" {plot_x + plot_w},{plot_y + plot_h}"

    tick_marks = []
    for idx in [0, 4, 8, 12, 16, 20, 24, 27]:
        x = plot_x + idx * step
        tick_marks.append(
            f'<text x="{x:.2f}" y="372" text-anchor="middle" font-size="14" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">{dates[idx].strftime("%m-%d")}</text>'
        )

    grid = []
    for i in range(5):
        gy = plot_y + i * (plot_h / 4)
        grid.append(f'<line x1="{plot_x}" y1="{gy:.2f}" x2="{plot_x + plot_w}" y2="{gy:.2f}" stroke="#e2e8f0" />')

    active_days = sum(1 for v in values if v > 0)
    total_events = sum(values)

    body = f"""
  <rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" rx="20" fill="#f8fafc" stroke="#e2e8f0" />
  {''.join(grid)}
  <polygon points="{area}" fill="#ffedd5" />
  <polyline points="{points}" fill="none" stroke="#f97316" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
  {''.join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#f97316" />' for x, y in pts)}
  {''.join(tick_marks)}
  <text x="36" y="390" font-size="18" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">Recent 28 days public activity · active days: {active_days} · total public events: {total_events}</text>
"""
    write_text(ASSETS / "activity-graph.svg", card_shell("Activity Graph", "Recent public activity from GitHub events", body))
    return active_days, total_events

def build_achievements(profile: dict, active_days: int, total_events: int) -> None:
    repos = int(profile.get("public_repos", 0) or 0)
    followers = int(profile.get("followers", 0) or 0)
    following = int(profile.get("following", 0) or 0)

    badges = [
        ("Seed Sower", repos >= 1, "Started building a visible public portfolio."),
        ("Steady Walker", active_days >= 3, "Kept showing up across multiple days."),
        ("Living Archive", total_events >= 5, "Left recent traces of work and progress."),
        ("Connected Signal", (followers + following) >= 1, "Your profile is linked to the wider community."),
    ]

    rows = []
    y = 126
    for idx, (name, unlocked, desc) in enumerate(badges):
        fill = "#eef2ff" if unlocked else "#f8fafc"
        dot = "#6366f1" if unlocked else "#cbd5e1"
        state = "Unlocked" if unlocked else "In Progress"
        yy = y + idx * 62
        rows.append(f"""
      <rect x="40" y="{yy}" width="1120" height="48" rx="18" fill="{fill}" stroke="#e2e8f0" />
      <circle cx="70" cy="{yy + 24}" r="9" fill="{dot}" />
      <text x="96" y="{yy + 20}" font-size="20" font-weight="700" fill="#0f172a" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">{escape(name)}</text>
      <text x="96" y="{yy + 38}" font-size="15" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">{escape(desc)}</text>
      <text x="1110" y="{yy + 30}" text-anchor="end" font-size="16" fill="#475569" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">{escape(state)}</text>
    """)

    body = "".join(rows) + '<text x="36" y="390" font-size="18" fill="#64748b" font-family="Inter, Pretendard, Apple SD Gothic Neo, Malgun Gothic, Segoe UI, sans-serif">Automatically refreshed from public profile signals.</text>'
    write_text(ASSETS / "achievements.svg", card_shell("Achievements", "Separate milestone cards for your profile", body))

def ensure_placeholders() -> None:
    placeholders = {
        "github-stats.svg": card_shell("GitHub Stats", "Placeholder", '<text x="36" y="170" font-size="22" fill="#64748b" font-family="Inter, sans-serif">Run the workflow once to load live values.</text>'),
        "activity-graph.svg": card_shell("Activity Graph", "Placeholder", '<text x="36" y="170" font-size="22" fill="#64748b" font-family="Inter, sans-serif">Run the workflow once to draw the recent public activity graph.</text>'),
        "achievements.svg": card_shell("Achievements", "Placeholder", '<text x="36" y="170" font-size="22" fill="#64748b" font-family="Inter, sans-serif">Run the workflow once to refresh milestone cards.</text>'),
    }
    for name, svg in placeholders.items():
        path = ASSETS / name
        if not path.exists():
            write_text(path, svg)

def main() -> None:
    make_greeting()
    select_banner()
    ensure_placeholders()

    username = os.environ.get("USERNAME", "").strip()
    if not username:
        return

    profile, events = safe_profile(username)
    build_stats(profile)
    active_days, total_events = build_graph(events)
    build_achievements(profile, active_days, total_events)

if __name__ == "__main__":
    main()
