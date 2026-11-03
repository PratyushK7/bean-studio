# yt_upload: one-time setup

The uploader uses the official YouTube Data API with **your own** Google Cloud project. Your password
never touches the script: you sign in once in the browser and a token is saved in `tools\.secrets\`.
Keep that folder private (never share or upload it).

## 1. Create the API project (about 10 min)
1. Go to https://console.cloud.google.com/ and sign in with the Google account that owns the channel.
2. Create a project, e.g. `bean-uploader`.
3. **APIs & Services → Library →** search **YouTube Data API v3 → Enable**.
4. **APIs & Services → OAuth consent screen** (or "Google Auth Platform"):
   - User type: **External**. App name: `bean-uploader`. Your email for support and developer contact.
   - Scopes: you can skip; the script asks for them.
   - **Test users → add your own Gmail.** (While the app is in "Testing", only test users can sign in.)
5. **Credentials → Create credentials → OAuth client ID → Application type: Desktop app.**
   Download the JSON and save it as:
   `C:\Users\praty\youtube\tools\.secrets\client_secret.json`

## 2. Sign in
```
cd C:\Users\praty\youtube
.venv\Scripts\python tools\yt_upload.py auth
```
Pick the channel's account. Google warns the app is unverified: that's your own app, click Continue.
The script prints the channel name when it worked.

Note: while the consent screen is in **Testing**, Google expires the sign-in after 7 days, so run
`auth` again when it asks. Setting the app to **In production** (no verification needed for your own use)
avoids that.

## 3. The audit (needed for scheduling to actually go public)
YouTube **locks every video uploaded from an unaudited API project as Private**, and a locked video
can't be scheduled or made public. To lift it, submit the free **YouTube API Services audit and quota
extension form**: https://support.google.com/youtube/contact/yt_api_form
Say it's a personal tool that uploads your own channel's videos. Approval usually takes days to a few weeks.
Until then, upload by hand in Studio using the `<project>-youtube.txt` sheet.

## 4. Daily use
```
.venv\Scripts\python tools\yt_upload.py upload nails --slot B --date 2026-11-05 --dry-run   # check
.venv\Scripts\python tools\yt_upload.py upload nails --slot B --date 2026-11-05             # send
.venv\Scripts\python tools\yt_upload.py status
```
Slots (IST): A 12:00, B 06:30, Long 21:30, the same as `bean-planner.xlsx`. Or give `--at "2026-11-05 18:00"`.

After it goes public: `yt_upload.py comment nails` posts the pinned-comment text; then pin it in Studio.
Still by hand: pinning, the Education "Type" field.

## Quota
A new project gets 10,000 units a day. One upload with thumbnail and captions uses about 2,000
(upload 1,600 + captions 400 + thumbnail 50, as published by Google; check the quota page if it changes),
so 2 Shorts a day fits.
