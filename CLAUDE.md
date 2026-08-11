# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CampusFind** is a Django-based social media platform (Instagram-style) with real-time chat. Users can sign up, create posts with images, like/comment on posts, follow other users, and exchange direct messages in real time via WebSockets.

## Tech Stack

- **Django 6.0.7** (project + apps)
- **Django Channels** (`daphne` for ASGI, `channels` for WebSocket support)
- **SQLite** for development (`db.sqlite3`)
- **Pillow** for image handling
- **Bootstrap 5.3.7** + Bootstrap Icons + Font Awesome 6.5.1 (CDN, served via `templates/base.html`)
- **Google Fonts (Poppins)** — loaded via CDN
- **Python 3.14** (virtualenv lives at `D:\social-media-project\.venv`)

## Running the Project

The repo is the inner `CampusFind/` directory of the larger `social-media-project/` repo. All Django commands run from `CampusFind/`.

```bash
# Activate venv (located one level up in D:\social-media-project\.venv)
source ../.venv/Scripts/activate      # Git Bash on Windows
# or: ../.venv/Scripts/activate       # PowerShell
# or: ../.venv/Scripts/activate.bat   # cmd

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser

# Start the dev server (HTTP + WebSocket via Daphne)
python manage.py runserver
# For WebSockets specifically (recommended for chat features):
daphne campusfind.asgi:application
```

There are **no automated tests** — both `posts/tests.py` and `chat/tests.py` are empty stubs. Manual testing via browser is the norm.

## URL Map

Root `campusfind/urls.py`:
- `/admin/` — Django admin
- `/` and all post/profile routes — `posts.urls` (home, profile, follow, like, comment)
- `/login/`, `/signup/`, `/logout/` — auth views in `campusfind.views`
- `/messages/...` — `chat.urls` (inbox, conversation, start-chat)
- `/media/...` — uploaded media (only in DEBUG)

WebSocket routes (`chat/routing.py`, mounted via `campusfind/asgi.py` under `AuthMiddlewareStack`):
- `ws://<host>/ws/chat/<conversation_id>/` → `ChatConsumer` (live message stream + sidebar broadcast)
- `ws://<host>/ws/sidebar/` → `SidebarConsumer` (per-user real-time sidebar updates)

## Architecture

### Project layout (`CampusFind/`)

```
campusfind/          # Django project (settings, root urls, asgi/wsgi, auth views)
posts/               # Core social media app (models, views, forms, signals)
chat/                # Real-time messaging app (consumers, models, views)
templates/           # Project-level templates (base.html, auth/, components/)
static/css/          # style.css (single stylesheet)
media/               # User uploads (posts/, profile_images/)
db.sqlite3           # Dev database
```

### Two apps, two layers

**`posts/`** — synchronous Django views handling the feed/profile/social graph:
- Models: `UserProfile` (auto-created via signal), `Post`, `Like` (unique constraint on `user+post`), `Comment` (max 300 chars, ordered by `created_at`), `Follow` (unique constraint, CheckConstraint blocks self-follows).
- Views query with `select_related`/`prefetch_related` for likes/comments and annotate `comment_count`. `is_liked` is set per-row by checking `post.likes.filter(user=request.user).exists()`.
- Posts/templates are organized as small partials in `posts/templates/posts/components/` (`post_card.html`, `post_modal.html`, `delete_modal.html`, `follow_modal.html`, `follow_user_item.html`) included by `home.html` and `profile.html`.
- A custom template filter `posts/templatetags/post_filters.py::instagram_date` produces relative timestamps ("Just now", "5 minutes ago", …).

**`chat/`** — WebSocket-first direct messaging:
- Models: `Conversation` (M2M participants, ordered by `-updated_at`), `Message`, `ConversationStatus` (one row per participant per conversation with `unread_count`).
- `ChatConsumer` (`chat/consumers.py`) joins two channel groups on connect: `chat_<conversation_id>` and `user_<user_id>`. On `receive`, it persists the message, bumps `ConversationStatus.unread_count` for the other participant (via `F('unread_count') + 1`), and broadcasts to both groups.
- `SidebarConsumer` is a per-user WebSocket that listens for `sidebar_update` events pushed by `ChatConsumer` whenever a new message arrives.
- The HTTP view `chat.views.messages_view` renders the conversation shell at `/messages/<id>/` and zeroes the receiver's `unread_count` on open. `start_chat` reuses or creates a 2-participant conversation.
- Channel layer is **in-memory** (`channels.layers.InMemoryChannelLayer`) — fine for dev, won't scale across processes.

### Signals

`posts/signals.py` registers `post_save` on `User` → auto-creates a `UserProfile`. Wired in `posts/apps.py::PostsConfig.ready()`.

### Auth flow

- Built-in `UserCreationForm` for signup (`campusfind/views.py::signup_view`).
- `LOGIN_URL = "/login/"`, `LOGIN_REDIRECT_URL = "/"`, `LOGOUT_REDIRECT_URL = "/login/"` (in `settings.py`).
- All feed/post/profile/chat views require login via `@login_required`.

### Templates

- Project-level `templates/base.html` defines the navbar + Bootstrap/JS includes. Auth pages (`templates/auth/login.html`, `signup.html`) extend their own minimal layout, not `base.html`.
- Each app owns its own `templates/<app>/` directory and renders paths like `posts/components/post_card.html` from `home.html`/`profile.html`.
- `templates/components/messages.html` renders Django's `messages` framework; auto-dismisses after 3s via inline JS in `base.html`.

## Common Operations

```bash
# After model changes
python manage.py makemigrations
python manage.py migrate

# Django shell
python manage.py shell

# Create admin user
python manage.py createsuperuser

# Collect static (for production)
python manage.py collectstatic
```

## Important Conventions

- All post/comment/follow/like redirects honor a hidden `next` form field (`request.POST.get("next")`) to return the user to the originating page; fall back to `home` or `userprofile`.
- Like and follow toggles delete + recreate rows rather than updating a flag — simple and idempotent given the unique constraints.
- Profile picture removal: `edit_profile` view checks `request.POST.get("remove_image") == "1"` and resets the field to the `profile_images/default.png` default.
- Image uploads go to `media/posts/` and `media/profile_images/`. The default profile picture lives at `media/profile_images/default.png` — needed for fresh installs.
- `DEBUG = True` and an insecure `SECRET_KEY` are committed to `settings.py`; only acceptable for local development. Do not deploy as-is.
- `ALLOWED_HOSTS = []` — adjust before any non-localhost deployment.