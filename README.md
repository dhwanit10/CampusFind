# CampusFind

A Django + Channels social-media platform with a real-time feed, follow graph, WebSocket chat, 24-hour stories, live notifications, and an AI caption-assist feature powered by a local Ollama model.

## Features

- **Auth** — username signup/login, profile pictures, bio editing.
- **Posts** — image uploads, captions, likes, comments, edit & delete.
- **Profile & social graph** — own profile page, follow / unfollow, follower / following lists, per-user post grids.
- **Search** — find users and posts by name or caption (`/search/?q=...`), with a search box in the navbar.
- **Stories** — 24-hour disappearing image posts in a horizontal strip at the top of the feed (`/story/create/`).
- **Real-time chat** — Django Channels WebSocket (`ws/chat/<id>/`) with sidebar updates (`ws/sidebar/`).
- **Live notifications** — bell icon in the navbar with a live-updating badge for likes, comments, follows, and messages. Updates push instantly over `ws/notifications/`.
- **AI caption suggestions** — "✨ Suggest" on the create-post page returns three caption rewrites, hashtags, and emoji from a local Ollama model. Falls back gracefully if Ollama is offline.

## Stack

- Django 6.0 + Channels (Daphne for ASGI)
- SQLite (development)
- Pillow for image handling
- Bootstrap 5 + Bootstrap Icons + Font Awesome (CDN)
- Ollama for AI caption suggestions (local; no API key)

## Quick start

```bash
# Activate the venv (lives one level up at ../.venv)
source ../.venv/Scripts/activate        # Git Bash
# or: ../.venv/Scripts/activate.bat     # cmd
# or: ..\.venv\Scripts\Activate.ps1      # PowerShell

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Run the dev server (HTTP + WebSocket)
python manage.py runserver
```

For WebSocket-heavy testing (chat, notifications) prefer Daphne:

```bash
daphne campusfind.asgi:application
```

## AI features (Ollama)

The "✨ Suggest" button on the create-post page calls a local Ollama HTTP API. Install and run Ollama once on your machine:

```bash
# Install from https://ollama.com, then:
ollama pull llama3.1:8b
ollama serve                # leave running in another terminal
```

The Django app uses these env vars (defaults shown):

```
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

If Ollama is unreachable or returns junk, the endpoint falls back to a static result so the UI never breaks.

## URL map

- `/admin/` — Django admin
- `/`, `/profile/`, `/user/<username>/`, `/post/...` — feed and post management (`posts.urls`)
- `/login/`, `/signup/`, `/logout/` — auth (`campusfind.views`)
- `/messages/`, `/messages/<id>/`, `/messages/start/<username>/` — chat (`chat.urls`)
- `/search/?q=...` — user and post search (`posts.urls`)
- `/notifications/`, `/notifications/read/` — notifications dropdown + mark-all-read (`notifications.urls`)
- `/story/create/`, `/story/strip/` — stories (`stories.urls`)

WebSocket routes (`AuthMiddlewareStack` in `campusfind/asgi.py`):

- `ws/chat/<conversation_id>/` — chat messages + sidebar updates
- `ws/sidebar/` — per-user inbox sidebar updates
- `ws/notifications/` — live notification pushes

## Project layout

```
campusfind/          # Django project (settings, urls, asgi)
posts/               # Feed, posts, likes, comments, follow graph
chat/                # Real-time chat (consumers, models)
stories/             # 24-hour stories + strip
notifications/       # Notifications model + WebSocket + dropdown
ai/                  # Ollama client + caption-suggest endpoint
templates/           # Project-level templates (base.html, auth/, components/)
static/css/          # style.css
media/               # User uploads (posts/, profile_images/, stories/)
```

## Notes

- `SECRET_KEY` and `DEBUG` in `settings.py` are committed defaults for local development. Replace with environment variables before deploying.
- The channel layer is in-memory (`channels.layers.InMemoryChannelLayer`) — fine for a single-process dev server, won't scale across workers.
- Default profile picture lives at `media/profile_images/default.png` and is required for fresh installs.
