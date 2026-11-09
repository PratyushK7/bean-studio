"""Channels: one Bean Studio, several YouTube channels, each with its own videos, planner, numbers, topics, sign-in and tools.

The first channel in config["channels"] is the home channel ("bean"): it keeps the paths the studio always used (data/, line-boil/,
bean-planner.xlsx, tools/.secrets/token.json), so nothing moves. Every other channel lives under channels/<id>/.

Which channel a request is about comes from the X-Channel header (or ?channel=). Code that runs outside a request (the background
syncs, a thread started by a click) says it with `with channels.using(cid):`. Anything unknown falls back to the home channel.
"""
import re, threading
from contextlib import contextmanager
from pathlib import Path

from flask import has_request_context, request

ALL_TOOLS = ["projects", "topics", "agent", "jobs", "settings"]
ID = re.compile(r"^[a-z][a-z0-9-]{0,24}$")
_tl = threading.local()
_raw = {"fn": lambda: {}}


def init(raw_cfg):
    """the studio gives this module the loader of the raw settings (no channel applied) once, at start"""
    _raw["fn"] = raw_cfg


def ids(c):
    return list((c.get("channels") or {}).keys())


def home(c):
    return (ids(c) or ["bean"])[0]


def current(c):
    """the channel this code is working for: using() first, then the request, then home"""
    cid = getattr(_tl, "cid", None)
    if cid is None and has_request_context():
        cid = request.headers.get("X-Channel") or request.args.get("channel")
    return cid if cid in (c.get("channels") or {}) else home(c)


@contextmanager
def using(cid):
    prev = getattr(_tl, "cid", None)
    _tl.cid = cid
    try: yield
    finally: _tl.cid = prev


def bound(fn, cid):
    """fn wrapped so it runs as channel cid (for a thread started from a click)"""
    def run(*a, **k):
        with using(cid): return fn(*a, **k)
    return run


def is_home(c, cid):
    return cid == home(c)


def base_dir(ROOT, c, cid=None):
    cid = cid or current(c)
    return ROOT if is_home(c, cid) else ROOT / "channels" / cid


def data_dir(ROOT, c, cid=None):
    return base_dir(ROOT, c, cid) / "data"


def token_path(ROOT, c, cid=None):
    cid = cid or current(c)
    s = ROOT / "tools" / ".secrets"
    return s / "token.json" if is_home(c, cid) else s / f"token-{cid}.json"


def data_for(ROOT):
    """the data folder of the channel this code is working for, under the ROOT it was registered with"""
    return data_dir(ROOT, _raw["fn"]())


def token_now(ROOT):
    """the sign-in file of the channel this code is working for"""
    return token_path(ROOT, _raw["fn"]())


def resolve(ROOT, c):
    """the settings for the current channel: the global ones with this channel's own on top"""
    cid = current(c)
    ch = (c.get("channels") or {}).get(cid) or {}
    out = dict(c, channel_id=cid)
    if not is_home(c, cid):                      # a new channel gets its own folders unless it names them
        base = ROOT / "channels" / cid
        out.update(projects_dir=str(base / "videos"), planner=str(base / "planner.xlsx"), hide_projects=[])
    for src, dst in (("name", "channel"), ("projects_dir", "projects_dir"), ("planner", "planner"), ("slots", "slots"),
                     ("topic_category", "topic_category"), ("topic_channels", "topic_channels"), ("hide_projects", "hide_projects"),
                     ("voice_file", "voice_file")):
        if ch.get(src) not in (None, ""): out[dst] = ch[src]
    out.setdefault("voice_file", "~/.claude/youtube/voice.md")
    out["language"] = ch.get("language") or "English"
    out["data_dir"] = str(data_dir(ROOT, c, cid))
    out["token_path"] = str(token_path(ROOT, c, cid))
    return out


def public(ROOT, c, token_exists):
    """what the page needs to draw the channel bar and decide which tabs to show"""
    rows = []
    for cid, ch in (c.get("channels") or {}).items():
        rows.append({"id": cid, "name": ch.get("name") or cid, "emoji": ch.get("emoji") or "📺", "color": ch.get("color") or "#1982c4",
                     "language": ch.get("language") or "English", "note": ch.get("note") or "",
                     "tools": [t for t in (ch.get("tools") or ALL_TOOLS) if t in ALL_TOOLS], "home": cid == home(c),
                     "connected": token_exists(token_path(ROOT, c, cid))})
    return rows


def add(c_raw, cid, name, language, emoji, color):
    """the channels dict with one more channel (the caller saves it); raises ValueError with a plain reason"""
    chs = dict(c_raw.get("channels") or {})
    if not ID.match(cid or ""): raise ValueError("the id must be lowercase letters, numbers and dashes, starting with a letter")
    if cid in chs: raise ValueError(f"there is already a channel with the id {cid}")
    chs[cid] = {"name": name, "language": language or "English", "emoji": emoji or "📺", "color": color or "#c0262d",
                "tools": [t for t in ALL_TOOLS if t != "topics"],
                "note": "Topics stay off until this channel has a video skill (a style that can make its videos)."}
    return chs


def make_dirs(ROOT, c, cid):
    b = base_dir(ROOT, c, cid)
    for p in (b / "data", b / "videos", b / "reports"): p.mkdir(parents=True, exist_ok=True)


class PerChannel:
    """a dict-like whose contents belong to the current channel: PerChannel(make)[key] reads the right channel's copy.
    Lets code that keeps one module-level STATE dict serve several channels without changing its call sites."""
    def __init__(self, make):
        self._make, self._d, self._lock = make, {}, threading.Lock()

    def _me(self):
        cid = current(_raw["fn"]())
        with self._lock:
            if cid not in self._d: self._d[cid] = self._make(cid)
            return self._d[cid]

    def __getitem__(self, k): return self._me()[k]
    def __setitem__(self, k, v): self._me()[k] = v
    def __contains__(self, k): return k in self._me()
    def get(self, k, d=None): return self._me().get(k, d)
    def update(self, *a, **k): self._me().update(*a, **k)
    def items(self): return self._me().items()
    def keys(self): return self._me().keys()
    def values(self): return self._me().values()
    def setdefault(self, k, d=None): return self._me().setdefault(k, d)
