# Complete Setup Guide
## Islamic Guide — Auto Post to Blogger with Gemini AI

---

## PHASE 1: Get Your API Keys (Do This First)

### Step 1.1 — Gemini API Key (Free)
```
1. Go to https://aistudio.google.com
2. Click "Get API Key" in top left
3. Click "Create API Key" → Select or create project
4. Copy the key (starts with "AIzaSy...")
```

### Step 1.2 — Google Cloud Project for Blogger
```
1. Go to https://console.cloud.google.com
2. Create a new project (or select existing)
3. Search → "Blogger API v3" → ENABLE
4. Go to "Credentials" in left menu
5. Click "Create Credentials" → "API Key"
   → Copy the key (AIzaSy...)
   → Click "Restrict Key" → Select "Blogger API v3"
6. Click "Create Credentials" → "OAuth client ID"
   → Application type: "Desktop app"
   → Name: "Blogger Auto Post"
   → Click "Create"
   → Download JSON → Open it, you will see:
     - client_id (ends with .apps.googleusercontent.com)
     - client_secret (starts with GOCSPX-)
```

### Step 1.3 — Get Your Blog ID
```
1. Go to https://www.blogger.com
2. Select your blog
3. Go to Settings → "Blog address" section
4. Click "See blog info" → Copy "Blog ID"
   (it's a long number like 1234567890123456789)
```

---

## PHASE 2: Install & Setup (PC or Phone)

### Option A: On Your Computer (Windows/Mac/Linux)

```bash
# 2A.1 — Download the project
git clone https://github.com/Shahadat900/blogger-auto-post.git
cd blogger-auto-post

# 2A.2 — Install Python packages
pip install -r requirements.txt

# 2A.3 — Create .env file
cp .env.example .env
```

### Option B: On Your Phone (Termux for Android)

```bash
# 2B.1 — Install Termux from F-Droid (not Play Store)
# 2B.2 — Open Termux, run one by one:

pkg update -y && pkg upgrade -y
pkg install -y python git cronie
pip install -r requirements.txt
git clone https://github.com/Shahadat900/blogger-auto-post.git
cd blogger-auto-post
cp .env.example .env
```

---

## PHASE 3: Connect Your Blogger Blog

### Step 3.1 — Verify Blog with API Key

```bash
python scripts/verify_blog.py
```

You will see:
```
=======================================================
  Connect Your Blogger Blog
=======================================================

Blog Name [My Awesome Blog]: Islamic Guide
Blog URL [https://myblog.blogspot.com]: https://islamicguide.blogspot.com
Blog ID: 1234567890123456789
API Key (AIzaSy...): AIzaSyABC123xyz...

Verifying blog connection...

  Blog Name: Islamic Guide
  Blog URL: https://islamicguide.blogspot.com
  Total Posts: 97

  Connection successful!
  Saved to config.json
```

### Step 3.2 — Get OAuth Refresh Token

```bash
python scripts/setup_oauth.py
```

You will see:
```
=======================================================
  Blogger OAuth Setup (One-Time)
=======================================================

Client ID: 12345.apps.googleusercontent.com
Client Secret: GOCSPX-abc123...

Opening browser for authorization...
```

→ A browser will open asking you to login to Google
→ Click "Continue" → Select your Blogger account
→ Click "Allow" (it may say "not verified" — that's OK)
→ You will see "Authentication complete" in browser
→ Go back to terminal

```
  OAuth Setup Complete!

  Client ID: 12345.apps.googleusercontent.com
  Client Secret: GOCSPX-abc123...
  Refresh Token: 1//0xABC123...

  Saved to .env
```

### Step 3.3 — Fill Your .env File

Open `.env` and check all values are filled:

```bash
nano .env
```

It should look like this:
```
GEMINI_API_KEY=AIzaSyABC123...
BLOGGER_CLIENT_ID=12345.apps.googleusercontent.com
BLOGGER_CLIENT_SECRET=GOCSPX-abc123...
BLOGGER_REFRESH_TOKEN=1//0xABC123...
BLOGGER_BLOG_ID=1234567890123456789
```

---

## PHASE 4: Test Locally

Run the poster manually to make sure everything works:

```bash
python scripts/main.py
```

You will see:
```
==================================================
  Islamic Guide - Auto Post System
  2026-06-06 10:30:00
==================================================

Topic #1: What to pack for Umrah: a complete checklist

[1/4] Generating article with Gemini...
  Title: 10 Things You Must Pack for Your First Umrah Trip
  Words: 1245

[2/4] Generating 2 image(s) with Gemini...
  Image 1 saved: temp_images/featured_1.png
  Image 2 saved: temp_images/featured_2.png

[3/4] Posting to Blogger...
  Post ID: 123456789
  URL: https://islamicguide.blogspot.com/2026/06/umrah-pack-list.html
  Published: 2026-06-06T10:31:00+00:00

[4/4] Advanced to next topic (index: 1)

DONE: '10 Things You Must Pack for Your First Umrah Trip' posted successfully!
```

If you see errors, check:

| Error | Fix |
|---|---|
| `No module named 'google'` | Run `pip install -r requirements.txt` |
| `GEMINI_API_KEY not set` | Add your key to `.env` file |
| `Missing OAuth env vars` | Run `python scripts/setup_oauth.py` |
| `Blogger API error: 404` | Check your Blog ID in config.json |
| `No image data in Gemini response` | Check GEMINI_API_KEY is correct |

---

## PHASE 5: Deploy to GitHub Actions (Auto Schedule)

Step-by-step with your actual values:

### 5.1 — Go to GitHub Secrets Page

Open this link:
```
https://github.com/Shahadat900/blogger-auto-post/settings/secrets/actions
```

### 5.2 — Click "New repository secret" 5 times

Add these **exact names** (case sensitive):

| # | Name | Value (example) |
|---|---|---|
| 1 | `GEMINI_API_KEY` | `AIzaSyABC123xyz...` |
| 2 | `BLOGGER_CLIENT_ID` | `12345.apps.googleusercontent.com` |
| 3 | `BLOGGER_CLIENT_SECRET` | `GOCSPX-abc123...` |
| 4 | `BLOGGER_REFRESH_TOKEN` | `1//0xABC123...` |
| 5 | `BLOGGER_BLOG_ID` | `1234567890123456789` |

### 5.3 — Push Latest State to GitHub

```bash
# Commit your config and posted log
git add config.json posted_log.json .env.example
git commit -m "setup: add blog config and env template"
git push origin main
```

### 5.4 — Verify Workflow is Running

```
1. Go to https://github.com/Shahadat900/blogger-auto-post
2. Click "Actions" tab (top menu)
3. You should see "Auto Post to Blogger" workflow
4. Green dot = running. Red dot = error. Click to see logs.
```

---

## PHASE 6: Auto-Post Schedule

The workflow runs automatically at:

| Run | Time (UTC) | Your Local Time |
|---|---|---|
| 1st | 8:00 AM UTC | → Check your timezone |
| 2nd | 8:00 PM UTC | → Check your timezone |

To change schedule: Edit `.github/workflows/auto-post.yml` line 5-6

Examples:
```yaml
# 1 post per day at 9 AM
- cron: '0 9 * * *'

# 3 posts per day
- cron: '0 6,12,18 * * *'

# 4 posts per day
- cron: '0 6,12,18,22 * * *'

# Every 6 hours
- cron: '0 */6 * * *'
```

---

## PHASE 7: Manage Your Topics

### View Current Index
```bash
python -c "import json; c=json.load(open('config.json')); print(f'Next topic #{c[\"current_index\"]+1}: {c[\"subtopics\"][c[\"current_index\"]]}')"
```

### Reset to Start
```bash
python -c "import json; c=json.load(open('config.json')); c['current_index']=0; json.dump(c,open('config.json','w'),indent=2); print('Reset to topic 1')"
```

### View Posted History
```bash
python -c "import json; p=json.load(open('posted_log.json')); [print(f'{i+1}. {v[\"title\"]} -> {v[\"url\"]}') for i,(k,v) in enumerate(p.items())]"
```

### Manually Skip a Topic
```bash
python -c "import json; c=json.load(open('config.json')); c['current_index']=(c['current_index']+1)%len(c['subtopics']); json.dump(c,open('config.json','w'),indent=2); print(f'Skipped to topic #{c[\"current_index\"]+1}')"
```

---

## PHASE 8: Phone (Termux) Cron Setup

After setup completes, schedule daily posts on phone:

```bash
# Install cron
pkg install cronie

# Start cron service
crond

# Edit crontab
crontab -e
```

Add this line:
```cron
0 8,20 * * * cd ~/blogger-auto-post && python scripts/main.py >> ~/blogger-auto-post/logs.txt 2>&1
```

Or use the quick script:
```bash
bash termux/run-local.sh
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Workflow not triggering | Check Actions tab → "Enable workflow" button |
| Post not publishing | Run `python scripts/main.py` locally to see exact error |
| "Refresh token expired" | Run `python scripts/setup_oauth.py` again |
| Gemini returns short article | Edit `prompts/article_prompt.txt` → increase min words |
| Images not generating | Model `gemini-2.0-flash-exp-image-generation` may need latest SDK |
| Topic rotation stopped | Check `config.json` → `current_index` |
| Want more topics | Edit `config.json` → `subtopics` array |
| Want different schedule | Edit `.github/workflows/auto-post.yml` → `cron` |

---

## File Reference

| File | What It Does |
|---|---|
| `scripts/main.py` | Main orchestrator — run this to post |
| `scripts/gemini_writer.py` | Calls Gemini API to write article |
| `scripts/image_generator.py` | Generates images with Gemini |
| `scripts/post_to_blogger.py` | Uploads & publishes to Blogger |
| `scripts/auth_helper.py` | Manages OAuth tokens |
| `scripts/verify_blog.py` | Connect blog with API Key |
| `scripts/setup_oauth.py` | Get OAuth refresh token (one-time) |
| `prompts/article_prompt.txt` | AI prompt template (customize freely) |
| `config.json` | Blog config + 30 subtopics |
| `posted_log.json` | Tracks what's been posted |
| `termux/setup-termux.sh` | Auto setup for Termux phone |
| `termux/run-local.sh` | Quick local run + git push |
