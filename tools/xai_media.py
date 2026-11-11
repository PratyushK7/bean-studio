"""xAI image and video calls for Decoding Vyapaar (standard library only). The key is read from tools/.secrets/xai_key.txt and sent only to api.x.ai.

    python tools/xai_media.py image <out.png> "<prompt>" [--ref ref.png]       text to image, or an edit of the reference image
    python tools/xai_media.py video <still.png> <out.mp4> "<motion prompt>" [--seconds 5] [--model grok-imagine-video-1.5-lite]

Field names beyond the documented ones (aspect_ratio, resolution) are tried and dropped if the API rejects them, so a changed API fails soft.
Every call prints what it cost to learn from (the response's usage block, if there is one), so the dashboard can be checked against it.
"""
import argparse, base64, json, sys, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.x.ai/v1"
IMAGE_MODEL = "grok-imagine-image-2.0"
VIDEO_MODEL = "grok-imagine-video-1.5-lite"


def key():
    p = ROOT / "tools/.secrets/xai_key.txt"
    if not p.exists(): sys.exit(f"missing {p}: save the xAI API key there as one line")
    return p.read_text(encoding="utf-8").strip()


def call(method, path, payload=None, optional=()):
    """JSON request; optional = payload fields that are dropped one by one if the API answers 400/422"""
    fields = dict(payload or {})
    while True:
        req = urllib.request.Request(API + path, json.dumps(fields).encode() if payload is not None else None, method=method,
                                     headers={"Authorization": "Bearer " + key(), "Content-Type": "application/json", "User-Agent": "decoding-vyapaar/1.0"})
        try:
            return json.loads(urllib.request.urlopen(req, timeout=300).read())
        except urllib.error.HTTPError as e:
            body = e.read()[:600].decode("utf-8", "replace")
            drop = next((f for f in optional if f in fields and e.code in (400, 422)), None)
            if drop:
                print(f"  (the API rejected '{drop}', retrying without it: {body[:160]})", file=sys.stderr); fields.pop(drop); continue
            sys.exit(f"xAI {method} {path} -> {e.code}: {body}")


def data_uri(p):
    p = Path(p); mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}[p.suffix[1:].lower()]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def fetch(url, out):
    req = urllib.request.Request(url, headers={"User-Agent": "decoding-vyapaar/1.0"})
    Path(out).write_bytes(urllib.request.urlopen(req, timeout=300).read())


def image(out, prompt, ref=None, aspect="16:9"):
    if ref:
        r = call("POST", "/images/edits", {"model": IMAGE_MODEL, "prompt": prompt, "image": {"url": data_uri(ref), "type": "image_url"}, "aspect_ratio": aspect}, optional=("aspect_ratio",))
    else:
        r = call("POST", "/images/generations", {"model": IMAGE_MODEL, "prompt": prompt, "aspect_ratio": aspect, "n": 1}, optional=("aspect_ratio", "n"))
    d = r["data"][0]
    if d.get("b64_json"): Path(out).write_bytes(base64.b64decode(d["b64_json"]))
    else: fetch(d["url"], out)
    print("wrote", out, "| usage:", json.dumps(r.get("usage", {}))[:200])


def video(still, out, prompt, seconds=5, model=VIDEO_MODEL, aspect="16:9"):
    r = call("POST", "/videos/generations", {"model": model, "prompt": prompt, "image": {"url": data_uri(still)}, "duration": int(seconds),
                                              "aspect_ratio": aspect, "resolution": "720p"}, optional=("resolution", "aspect_ratio"))
    rid = r["request_id"]; t0 = time.time()
    while True:
        s = call("GET", f"/videos/{rid}")
        st = s.get("status")
        if st == "done": break
        if st in ("failed", "expired"): sys.exit(f"video {st}: {json.dumps(s)[:400]}")
        if time.time() - t0 > 900: sys.exit("video timed out after 15 minutes")
        time.sleep(5)
    fetch(s["video"]["url"], out)
    print("wrote", out, f"| {time.time() - t0:.0f} s to render | usage:", json.dumps(s.get("usage", {}))[:200])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("image"); a.add_argument("out"); a.add_argument("prompt"); a.add_argument("--ref")
    b = sub.add_parser("video"); b.add_argument("still"); b.add_argument("out"); b.add_argument("prompt"); b.add_argument("--seconds", default=5); b.add_argument("--model", default=VIDEO_MODEL)
    x = ap.parse_args()
    if x.cmd == "image": image(x.out, x.prompt, x.ref)
    else: video(x.still, x.out, x.prompt, x.seconds, x.model)
