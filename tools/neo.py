"""Tiny client for BrowserOS neo's local MCP server (http://127.0.0.1:9010/mcp): neo.py list | call <tool> '<json args>'
Used because the tools may not be loaded into a Claude Code session started before neo was added."""
import json, sys, urllib.request
URL = "http://127.0.0.1:9010/mcp"
H = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

def post(body, sid=None):
    h = dict(H); 
    if sid: h["mcp-session-id"] = sid
    r = urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(), h), timeout=120)
    txt = r.read().decode("utf-8", "replace"); out = None
    for line in txt.splitlines():
        if line.startswith("data: {"): out = json.loads(line[6:])
    return r.headers.get("mcp-session-id"), out

import os, tempfile
SIDFILE = os.path.join(tempfile.gettempdir(), "neo-session-id.txt")

def session():
    try:
        sid = open(SIDFILE).read().strip()
        if sid:
            post({"jsonrpc": "2.0", "id": 9, "method": "tools/list"}, sid); return sid          # still alive
    except Exception: pass
    sid, _ = post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "claude", "version": "1.0"}}})
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    open(SIDFILE, "w").write(sid or "")
    return sid

def call(tool, args, sid=None):
    sid = sid or session()
    return post({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": tool, "arguments": args}}, sid)[1]

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "list":
        sid = session(); res = post({"jsonrpc": "2.0", "id": 3, "method": "tools/list"}, sid)[1]
        for t in res["result"]["tools"]: print(t["name"], "-", (t.get("description") or "")[:110].replace("\n", " "))
    else:
        r = call(sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else {})
        for c in (r.get("result", r).get("content") or []): print(c.get("text", "")[:6000])
        if "error" in r: print(r["error"])
