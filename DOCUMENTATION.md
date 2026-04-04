# Creative Spotlight — Technical Documentation

**Repository:** `jadegold55/creative-spotlight`
**Branch:** `main`
**Last reviewed:** April 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Repository Structure](#3-repository-structure)
4. [Discord Bot (Python)](#4-discord-bot-python)
   - [Entry Point & Boot Sequence](#41-entry-point--boot-sequence)
   - [Configuration](#42-configuration)
   - [API Helper](#43-api-helper)
   - [Commands (Cogs)](#44-commands-cogs)
   - [Scraping](#45-scraping)
5. [Backend (Spring Boot)](#5-backend-spring-boot)
   - [Security & Auth](#51-security--auth)
   - [REST API Endpoints](#52-rest-api-endpoints)
   - [Services](#53-services)
   - [Repositories](#54-repositories)
   - [Data Models](#55-data-models)
   - [DTOs](#56-dtos)
   - [Exception Handling](#57-exception-handling)
6. [Database](#6-database)
7. [Infrastructure](#7-infrastructure)
   - [Docker Compose](#71-docker-compose)
   - [Dockerfiles](#72-dockerfiles)
   - [Nginx](#73-nginx)
8. [Dependencies](#8-dependencies)
9. [Environment Variables](#9-environment-variables)
10. [Request Flow Walkthroughs](#10-request-flow-walkthroughs)
11. [Pending Work & Known TODOs](#11-pending-work--known-todos)

---

## 1. Project Overview

Creative Spotlight is a multi-server Discord bot platform built for showcasing creative submissions — primarily art/images — with gallery browsing, voting, and scheduled contest features. The system is structured as three long-running services:

- **Discord Bot** — Python process handling all user-facing Discord interactions
- **Spring Boot Backend** — Java REST API managing persistence and business logic
- **PostgreSQL** — relational database storing images, votes, and per-guild configuration

A **Next.js frontend** is scaffolded but not yet functional. Deployment is on an AWS EC2 `t2.micro` instance via Docker Compose with Nginx as a reverse proxy, automated through GitHub Actions CI/CD.

---

## 2. System Architecture

```
Discord API
    │
    ▼
Discord Bot (Python)
    │  aiohttp + Bearer token
    ▼
Nginx (port 80)
    │  reverse proxy
    ▼
Spring Boot Backend (port 8080)
    │  Spring Data JPA
    ▼
PostgreSQL (port 5432)
```

**Public access:** Only `GET /images/{id}/file` is publicly reachable through Nginx. All other backend routes are locked to the Docker internal network, meaning only the bot container can reach them.

**Auth flow:** The bot attaches `Authorization: Bearer <API_SERVICE_TOKEN>` on every request. The backend's `ServiceTokenFilter` validates this token and grants `ROLE_BOT` to the Spring Security context before the request reaches any controller.

---

## 3. Repository Structure

```
creative-spotlight/
├── bot/                        # Python Discord bot
│   ├── main.py                 # Entry point, bot bootstrap
│   ├── config.py               # Env var loading
│   ├── __init__.py
│   ├── apihelper/
│   │   └── api.py              # Shared aiohttp client (get/post/delete)
│   ├── commands/               # Discord cogs, auto-loaded
│   │   ├── gallery.py          # /gallery, /upload, /delete
│   │   ├── setup.py            # /setup poems|contest|reset
│   │   ├── daily.py            # Daily poem loop (per-guild)
│   │   ├── contest.py          # Weekly contest loop (per-guild)
│   │   ├── poems.py            # /poem command
│   │   └── art.py              # Legacy file (superseded by gallery.py)
│   └── scraping/
│       ├── randompoem.py       # PoetryDB API scraper
│       └── artsearch.py        # Stub (empty)
│
├── backend/                    # Spring Boot Java backend
│   ├── src/main/java/com/discord/bot/
│   │   ├── BotApplication.java
│   │   ├── Config/
│   │   │   └── SecurityConfig.java
│   │   ├── Controller/
│   │   │   ├── GalleryImageController.java
│   │   │   └── GuildSettingsController.java
│   │   ├── Service/
│   │   │   ├── GalleryImageService.java
│   │   │   ├── GalleryImageVoteService.java
│   │   │   └── GuildSettingsService.java
│   │   ├── Repository/
│   │   │   ├── GalleryImageRepo.java
│   │   │   ├── GalleryImageVoteRepo.java
│   │   │   └── GuildSettingsRepo.java
│   │   ├── model/
│   │   │   ├── GalleryImage.java
│   │   │   ├── GalleryImageVote.java
│   │   │   ├── GuildSettings.java
│   │   │   ├── Poem.java
│   │   │   ├── PoemVote.java
│   │   │   └── ContestWinner.java   (POJO, not an entity)
│   │   ├── dto/
│   │   │   ├── GalleryImageResponse.java
│   │   │   ├── GuildSettingsResponse.java
│   │   │   ├── SetupPoemsRequest.java
│   │   │   ├── SetupContestRequest.java
│   │   │   ├── SetupChannelsRequest.java
│   │   │   └── ApiError.java
│   │   ├── Filter/
│   │   │   ├── ServiceTokenFilter.java   (active)
│   │   │   └── RateLimitFilter.java      (commented out)
│   │   └── Exceptions/
│   │       ├── GlobalExceptionHandler.java
│   │       └── InvalidVote.java
│   └── pom.xml
│
├── frontend/                   # Next.js scaffold (not yet functional)
│   ├── app/
│   │   ├── page.tsx
│   │   └── layout.tsx
│   └── package.json
│
├── docker-compose.yml
├── nginx.conf
├── Dockerfile                  # Bot image
├── requirements.txt            # Bot Python deps
├── scripts/
│   ├── load-secrets.ps1        # Local dev secret loading (PowerShell)
│   └── load-secrets.sh
└── tests/
    └── test_scraper.py
```

---

## 4. Discord Bot (Python)

### 4.1 Entry Point & Boot Sequence

**`bot/main.py`**

Defines `MyBot`, a subclass of `commands.Bot`. On startup it runs `setup_hook()` which iterates every `.py` file in `bot/commands/` and calls `self.load_extension(f"bot.commands.{filename}")`. This means any new cog file dropped into `commands/` is automatically loaded — no manual registration needed.

Once the bot is connected (`on_ready`), it calls `self.tree.copy_global_to(guild=...)` then `self.tree.sync(guild=...)` to register slash commands to the configured guild. Guild-scoped syncing takes effect immediately during development; global syncing can take up to an hour.

```
startup
  └─ setup_hook()
       ├─ load_extension("bot.commands.gallery")
       ├─ load_extension("bot.commands.setup")
       ├─ load_extension("bot.commands.daily")
       ├─ load_extension("bot.commands.contest")
       ├─ load_extension("bot.commands.poems")
       └─ load_extension("bot.commands.art")   ← legacy
  └─ on_ready()
       └─ tree.sync(guild=GUILD_ID)
```

### 4.2 Configuration

**`bot/config.py`**

All config is read from environment variables via `python-dotenv`:

| Variable | Purpose |
|---|---|
| `TOKEN` | Discord bot token |
| `BACKEND_URL` | Base URL for the Spring Boot API (e.g. `http://backend:8080`) |
| `PUBLIC_URL` | Publicly reachable URL for serving image files (used in embeds) |
| `API_SERVICE_TOKEN` | Shared secret sent as `Bearer` token to authenticate with the backend |

### 4.3 API Helper

**`bot/apihelper/api.py`**

Manages a single shared `aiohttp.ClientSession` across the entire bot process. The session is created lazily on first use and re-created if closed. Every request automatically includes `Authorization: Bearer <API_SERVICE_TOKEN>`.

Three async functions are exposed:

- `get(path, params, headers)` — returns parsed JSON on 200, or `None` on any other status
- `post(path, params, data, headers)` — returns `(status_code, response_text)`
- `delete(path, params, headers)` — returns `(status_code, response_text)`

`close_session()` should be called on bot shutdown to cleanly drain the session.

### 4.4 Commands (Cogs)

Each file in `bot/commands/` is a `commands.Cog` and must export an `async def setup(bot)` function that calls `bot.add_cog(...)`. This is the contract required by `load_extension`.

---

#### `gallery.py` — Gallery Cog

**`/gallery`** — Cooldown: 1 use per 5 seconds per user per guild. Ephemeral response.

1. `defer(thinking=True, ephemeral=True)`
2. `GET images/all?guildid={guild.id}`
3. Groups returned images by `groupId` using `group_images_into_posts()`. Images sharing a `groupId` represent a multi-image submission uploaded together.
4. Renders a `GalleryViewer` (a `LayoutView`) containing a `TextDisplay` (title, uploader mention, vote count), a `MediaGallery` of the current post's images, and an `ActionRow` with Previous / ❤️ / Next buttons.
5. Navigation buttons rebuild the view components in-place and call `interaction.response.edit_message(view=self)`.
6. The vote button calls `POST images/{id}/vote?userID={user.id}`. On 409 (already voted), sends an ephemeral "already voted" message. On success, increments `voteCount` in local state and rebuilds the view.

Image URLs in the `MediaGallery` use `{PUBLIC_URL}/images/{id}/file` — the publicly accessible endpoint that bypasses Nginx's internal-only restriction.

**`/upload`** — Cooldown: 1 use per 30 seconds per user per guild. Accepts `title` (required) and up to 4 file attachments.

1. Validates all attachments have an `image/*` content type.
2. Downloads all attachments concurrently using a temporary `aiohttp.ClientSession`.
3. If 1 file: builds a `FormData` with field `"file"` and POSTs to `images/add`.
4. If 2-4 files: builds a `FormData` with multiple `"files"` fields and POSTs to `images/add-multiple`. The backend assigns a shared `groupId` UUID, grouping them as a single post in the gallery.

**`/delete`** — Cooldown: 1 use per 30 seconds per user per guild. Ephemeral.

1. `GET images/user/{user.id}?guildid={guild.id}` to fetch the user's own submissions.
2. Renders a `DeleteView` with a `Select` menu listing up to 25 of their submissions.
3. On selection, calls `DELETE images/{image_id}`. Expects 204 on success.

---

#### `setup.py` — Setup Cog

All commands require `administrator` permission. All responses are ephemeral.

**`/setup poems <channel>`**

Shows a `TimeSetupView` — a `View` with four dropdowns (Hour 1-12, Minute :00/:15/:30/:45, AM/PM, Timezone) and a Confirm button. On confirm, converts to 24-hour time and calls:

`POST guilds/{guildId}/setup-poems?poemChannelId=&hour=&minute=&timezone=`

**`/setup contest <channel> <day> <duration>`**

`day` is a choice from Monday (0) to Sunday (6). `duration` is 1-14 days. Shows the same `TimeSetupView`. On confirm:

`POST guilds/{guildId}/setup-contest?spotlightChannelId=&day=&hour=&minute=&timezone=&durationDays=`

**`/setup reset <feature>`**

`feature` is either `"poems"` or `"contest"`. Sends:

- `DELETE guilds/{guildId}/setup-poems`
- `DELETE guilds/{guildId}/setup-contest`

This nulls out the relevant fields in `GuildSettings`, which stops the daily/contest loops from targeting that guild.

---

#### `daily.py` — Daily Poem Loop

Runs entirely as a background `asyncio.Task` started in `cog_load`. No slash command.

**Loop behavior:**

1. `GET guilds/with-poems` to get all guilds that have a poem channel configured.
2. For each guild, computes the next UTC datetime for that guild's configured hour/minute/timezone using `_next_daily()`.
3. Sorts all upcoming events and sleeps until the nearest one (`discord.utils.sleep_until`).
4. When the time fires, calls `scrape()` (PoetryDB) and sends an `@everyone` embed to the configured channel.
5. Loops. If no guilds are configured, sleeps 60 seconds before retrying.

---

#### `contest.py` — Spotlight / Contest Loop

Runs as a background `asyncio.Task`. No slash command — announcements are fully automated.

**`active_contests` dict:** `{guild_id: (end_utc, guild_data)}` — tracks which guilds currently have an in-progress contest so the loop can schedule the end event.

**Loop behavior:**

1. `GET guilds/with-spotlight` to get all guilds with spotlight channel configured.
2. For each guild: if `gid` is in `active_contests`, schedule an `"end"` event at `end_utc`; otherwise compute the next weekly occurrence of the configured day/hour/minute/timezone using `_next_weekly()` and schedule a `"start"` event.
3. Sorts all events and sleeps until the nearest one.
4. On `"start"`: sends a `Contest` LayoutView announcement to the spotlight channel, records `(end_time, guild)` in `active_contests`.
5. On `"end"`: calls `GET /images/contest/winner?guildid=...`, sends a winner embed, removes from `active_contests`.

**`Contest` LayoutView:** Displays a text block with contest title, description, and deadline. Contains a disabled `"signup"` button (signup flow is a pending TODO).

---

#### `poems.py` — Poetry Cog

**`/poem [author] [title]`**

Calls `scrape(author, title)` from `randompoem.py` and renders the result in a Discord embed. Public (non-ephemeral). No backend call.

---

#### `art.py` — Art Cog

**`/art`** — Cooldown: 1 use per 5 seconds per user per guild. Ephemeral.

Calls `scrapeArt()` from `bot/scraping/artsearch.py` in a thread (`asyncio.to_thread`) to fetch a random piece of art from an external source. Downloads the image bytes via `aiohttp` with a custom `User-Agent` header (IIIF-style image URLs require this), then sends it as a `discord.File` attachment alongside an embed showing the title, artist, and date.

---

### 4.5 Scraping

**`bot/scraping/randompoem.py`**

`scrape(author=None, title=None)` — hits the [PoetryDB](https://poetrydb.org) public API:

- With `author`: `GET /author,linecount/{author};{random_4-20}`
- With `title`: `GET /title/{title}`
- Default: `GET /linecount/15`

Returns `{title, author, content}` from a randomly selected poem in the result set, or `None` on empty/error. Used by both the `/poem` command and the daily poem loop.

**`bot/scraping/artsearch.py`** — empty stub.

---

## 5. Backend (Spring Boot)

**Language:** Java 21
**Framework:** Spring Boot 3.4.3
**Build:** Maven (multi-stage Docker build)

### 5.1 Security & Auth

**`SecurityConfig.java`**

```
Request
  └─ ServiceTokenFilter (runs before UsernamePasswordAuthenticationFilter)
       ├─ /actuator/health  →  skip filter (public)
       ├─ GET /images/*/file  →  skip filter (public)
       └─ all others:
            ├─ no Authorization header  →  401
            ├─ token mismatch  →  401
            └─ token matches  →  set ROLE_BOT in SecurityContext → proceed
```

Spring Security then enforces `.anyRequest().hasRole("BOT")` — so if the filter doesn't set the auth context, the request is rejected at the security layer too.

CSRF is disabled (stateless API). HTTP Basic is configured (`httpBasic(Customizer.withDefaults())`) to support future frontend OAuth alongside the current token auth, but in practice only the Bearer token filter is active for bot traffic.

**`ServiceTokenFilter.java`**

Extends `OncePerRequestFilter`. Reads `Authorization: Bearer <token>` header, validates against `${api.service.token}`, and if valid creates a `UsernamePasswordAuthenticationToken` with `ROLE_BOT` authority, sets it in `SecurityContextHolder`, then clears it in a `finally` block after the chain runs.

**`RateLimitFilter.java`**

Entirely commented out. Was a per-user `Bucket4j` + Caffeine in-memory rate limiter. Replaced by Nginx-level rate limiting. The `bucket4j-core` and `caffeine` dependencies remain in `pom.xml`.

---

### 5.2 REST API Endpoints

#### `/images` — `GalleryImageController`

| Method | Path | Auth | Description | Response |
|---|---|---|---|---|
| GET | `/images/{id}` | BOT | Get image metadata + vote count | `GalleryImageResponse` |
| GET | `/images/{id}/file` | Public | Serve raw image bytes | `byte[]` + Content-Type header |
| GET | `/images/{id}/votes` | BOT | Get vote count for image | `Long` |
| GET | `/images/all?guildid=` | BOT | Get all images for a guild (with vote counts) | `List<GalleryImageResponse>` |
| GET | `/images/contest/winner?guildid=` | BOT | Get image with most votes for a guild | `ContestWinner` |
| GET | `/images/user/{uploaderid}?guildid=` | BOT | Get all images uploaded by a specific user in a guild | `List<GalleryImageResponse>` |
| POST | `/images/add` | BOT | Upload a single image (multipart) | `201 GalleryImageResponse` |
| POST | `/images/add-multiple` | BOT | Upload multiple images as a group (multipart) | `201 List<GalleryImageResponse>` |
| POST | `/images/{id}/vote?userID=` | BOT | Cast a vote; 409 if already voted | `202 Void` |
| DELETE | `/images/{id}` | BOT | Delete image | `204 Void` |

**`/images/add` multipart fields:** `file` (binary), `uploaderid` (Long, required), `guildid` (Long, required), `title` (String, optional)

**`/images/add-multiple` multipart fields:** `files[]` (binary, multiple), `uploaderid`, `guildid`, `title`

---

#### `/guilds` — `GuildSettingsController`

| Method | Path | Auth | Description | Response |
|---|---|---|---|---|
| GET | `/guilds/{guildId}` | BOT | Get all settings for a guild | `GuildSettingsResponse` |
| POST | `/guilds/{guildId}/setup-poems` | BOT | Configure daily poem channel + schedule | `GuildSettingsResponse` |
| POST | `/guilds/{guildId}/setup-contest` | BOT | Configure weekly contest channel + schedule | `GuildSettingsResponse` |
| POST | `/guilds/{guildId}/setup` | BOT | Set channel IDs only (no schedule) | `GuildSettingsResponse` |
| GET | `/guilds/with-spotlight` | BOT | Get all guilds that have a spotlight channel configured | `List<GuildSettingsResponse>` |
| GET | `/guilds/with-poems` | BOT | Get all guilds that have a poem channel configured | `List<GuildSettingsResponse>` |
| DELETE | `/guilds/{guildId}/setup-poems` | BOT | Remove poem configuration | `200 Void` |
| DELETE | `/guilds/{guildId}/setup-contest` | BOT | Remove contest configuration | `200 Void` |

**`setup-poems` query params:** `poemChannelId`, `hour` (0-23), `minute`, `timezone` (IANA string)

**`setup-contest` query params:** `spotlightChannelId`, `day` (0=Mon, 6=Sun), `hour`, `minute`, `timezone`, `durationDays` (1-14)

---

#### Other

| Path | Auth | Description |
|---|---|---|
| GET `/actuator/health` | Public | Spring Boot health check |

---

### 5.3 Services

#### `GalleryImageService`

The primary orchestrator for image operations. Depends on `GalleryImageRepo` and `GalleryImageVoteService`.

- `getImage(id)` — fetches entity, gets vote count separately, returns `GalleryImageResponse`
- `getAllImages(guildId)` — delegates to `findByGuildidWithVotes` (JPQL with LEFT JOIN + COUNT aggregation in a single query, returns DTOs directly)
- `getContestWinner(guildId)` — calls `GalleryImageVoteService.getWinningImage(guildId)`, wraps result in `ContestWinner`; throws 404 if no votes
- `getImagesByUploader(uploaderId, guildId)` — fetches entities, maps each to DTO with individual vote count
- `addImage(file, uploaderId, guildId, title)` — reads `MultipartFile` bytes, constructs `GalleryImage` (auto-assigns a `groupId` UUID), saves
- `addImages(files, uploaderId, guildId, title)` — assigns one shared `groupId` UUID across all files, saves each individually
- `vote(id, userId)` — delegates to `GalleryImageVoteService.addVote()`
- `deleteImage(id)` — cascades to `GalleryImageVote` rows via `CascadeType.ALL, orphanRemoval = true`

#### `GalleryImageVoteService`

- `addVote(userId, image)` — checks for existing vote via `findByUserIDAndGalleryImage`; if found, throws `InvalidVote` (→ 409). Otherwise saves new `GalleryImageVote`.
- `getVoteCount(image)` — `countByGalleryImage`
- `getWinningImage(guildId)` — `findWinningImagesByGuild` with `PageRequest.of(0, 1)` to get the single top-voted image

#### `GuildSettingsService`

- All setup methods use `getOrCreate(guildId)` — tries `findById`, falls back to `new GuildSettings(guildId, null, null)` — enabling upsert behavior without explicit `MERGE` SQL.
- `deletePoemsSetup` / `deleteContestSetup` — nulls out the relevant fields and saves. The bot loops check for non-null channel IDs, so nulling them effectively disables the feature.
- `getGuildsWithSpotlight()` / `getGuildsWithPoems()` — used by the bot's background loops to know which guilds to schedule events for.

---

### 5.4 Repositories

All extend `JpaRepository`, giving standard CRUD for free.

**`GalleryImageRepo`**

- `findByGuildid(Long)` — standard derived query
- `findByGuildidWithVotes(Long)` — custom JPQL: `SELECT new GalleryImageResponse(..., COUNT(v), ...) FROM GalleryImage i LEFT JOIN GalleryImageVote v ON v.galleryImage = i WHERE i.guildid = :guildid GROUP BY i.id, ...` — returns DTOs with vote counts in a single round trip
- `findByUploaderIDAndGuildid(Long, Long)` — derived query

**`GalleryImageVoteRepo`**

- `findByUserIDAndGalleryImage(Long, GalleryImage)` — duplicate vote check
- `countByGalleryImage(GalleryImage)` — vote count
- `findWinningImages(Pageable)` — `GROUP BY galleryImage ORDER BY COUNT(v) DESC` (global, no guild filter)
- `findWinningImagesByGuild(Long, Pageable)` — same query filtered by `guildid`

**`GuildSettingsRepo`**

- `findBySpotlightChannelIdIsNotNull()` — guilds with contest configured
- `findByPoemChannelIdIsNotNull()` — guilds with poems configured

---

### 5.5 Data Models

#### `GalleryImage` (entity)

| Field | Type | Notes |
|---|---|---|
| `id` | Long | PK, auto-generated |
| `uploaderID` | Long | Discord user ID |
| `guildid` | Long | Discord guild ID |
| `uploadedAt` | LocalDateTime | Set at construction |
| `contentType` | String | MIME type (e.g. `image/png`) |
| `title` | String | Set by uploader |
| `groupId` | String | UUID grouping multi-image posts |
| `imageData` | byte[] | Raw binary, stored as `bytea` in Postgres. Annotated `@JsonIgnore` — never serialized in API responses. |
| `votes` | List\<GalleryImageVote\> | OneToMany, CascadeType.ALL, orphanRemoval=true |

Two constructors: one auto-generates `groupId`, one accepts an explicit `groupId` (used by `addImages` to group a multi-upload batch under one ID).

#### `GalleryImageVote` (entity)

| Field | Type | Notes |
|---|---|---|
| `id` | Long | PK, auto-generated |
| `galleryImage` | GalleryImage | ManyToOne FK |
| `userID` | Long | Discord user ID |

Table-level unique constraint on `(gallery_image_id, userID)` — enforces one vote per user per image at the DB level.

#### `GuildSettings` (entity)

| Field | Type | Notes |
|---|---|---|
| `guildId` | Long | PK (Discord guild ID) |
| `spotlightChannelId` | Long | Channel for contest announcements |
| `poemChannelId` | Long | Channel for daily poems |
| `poemHour` | Integer | 0-23 |
| `poemMinute` | Integer | 0-59 |
| `poemTimezone` | String | IANA timezone string |
| `contestDay` | Integer | 0=Mon, 6=Sun |
| `contestHour` | Integer | 0-23 |
| `contestMinute` | Integer | 0-59 |
| `contestTimezone` | String | IANA timezone string |
| `contestDurationDays` | Integer | 1-14 |

#### `ContestWinner` (POJO, not an entity)

Returned by `GET /images/contest/winner`. Fields: `id`, `uploaderid`, `votes`.

#### `Poem`, `PoemVote` (entities, no controller yet)

Models exist with their repositories (`PoemRepo`, `PoemVoteRepo`) but no controller or service has been wired up yet.

---

### 5.6 DTOs

**`GalleryImageResponse`** (record): `id, uploaderId, guildId, title, contentType, uploadedAt, voteCount, groupId`

Note: `imageData` is intentionally excluded from this DTO. The raw bytes are only served via `GET /images/{id}/file`.

**`GuildSettingsResponse`** (record): mirrors all `GuildSettings` fields. Has a static factory `GuildSettingsResponse.from(GuildSettings)`.

**`ApiError`** (record): `timestamp (Instant), status (int), code (String), message (String), path (String)` — returned by the global exception handler.

**`SetupPoemsRequest`** (record): `poemChannelId, hour, minute, timezone`

**`SetupContestRequest`** (record): `spotlightChannelId, day, hour, minute, timezone, durationDays`

**`SetupChannelsRequest`** (record): `poemChannelId, spotlightChannelId`

---

### 5.7 Exception Handling

`GlobalExceptionHandler` (`@RestControllerAdvice`) maps all exceptions to `ApiError` JSON responses:

| Exception | HTTP Status | Code |
|---|---|---|
| `InvalidVote` | 409 Conflict | `INVALID_VOTE` |
| `MethodArgumentNotValidException` | 400 Bad Request | `VALIDATION_ERROR` |
| `ConstraintViolationException` | 400 Bad Request | `VALIDATION_ERROR` |
| `ResponseStatusException` | mapped from exception | `REQUEST_ERROR` |
| Any other `Exception` | 500 Internal Server Error | `INTERNAL_ERROR` |

---

## 6. Database

**Engine:** PostgreSQL 16

**Schema management:** Currently via `SPRING_JPA_HIBERNATE_DDL_AUTO=update` (Hibernate auto-updates). Migration to Flyway is documented and planned (see `docs/db migration.md`).

### Tables

**`gallery_image`**

| Column | Type |
|---|---|
| id | BIGSERIAL PK |
| uploader_id | BIGINT |
| guild_id | BIGINT |
| uploaded_at | TIMESTAMP |
| content_type | VARCHAR |
| title | VARCHAR |
| group_id | VARCHAR |
| image_data | BYTEA |

**`gallery_image_votes`**

| Column | Type |
|---|---|
| id | BIGSERIAL PK |
| gallery_image_id | BIGINT FK → gallery_image.id |
| user_id | BIGINT |
| UNIQUE | (gallery_image_id, user_id) |

**`guild_settings`**

| Column | Type |
|---|---|
| guild_id | BIGINT PK |
| spotlight_channel_id | BIGINT nullable |
| poem_channel_id | BIGINT nullable |
| poem_hour | INTEGER nullable |
| poem_minute | INTEGER nullable |
| poem_timezone | VARCHAR nullable |
| contest_day | INTEGER nullable |
| contest_hour | INTEGER nullable |
| contest_minute | INTEGER nullable |
| contest_timezone | VARCHAR nullable |
| contest_duration_days | INTEGER nullable |

**`poem`**, **`poem_votes`** — exist per entity definitions, no application logic wired yet.

### Persistence Notes

- Image binary data is stored directly in the database as `BYTEA`. There is no S3 or file system storage.
- Docker volume `postgres_data` persists the database across container restarts. `docker compose down -v` removes it.
- `docker system prune -af` removes images but does not touch named volumes. `docker image prune -f` removes only dangling images and is safe for routine use.

---

## 7. Infrastructure

### 7.1 Docker Compose

**`docker-compose.yml`** defines three services with an explicit startup dependency chain:

```
db  →  backend  →  bot
```

| Service | Image | Ports | Notes |
|---|---|---|---|
| `db` | `postgres:16` | `${PORTS}` (env-configured) | Named volume `postgres_data` |
| `backend` | Built from `./backend/Dockerfile` | `8080:8080` | Depends on `db` |
| `bot` | Built from root `./Dockerfile` | None | Depends on `backend`; `BACKEND_URL=http://backend:8080` |

The `BACKEND_URL` inside Docker uses the service name `backend` as the hostname — internal Docker DNS resolves this. `PUBLIC_URL` must be the externally accessible URL (EC2 public IP or domain) for image embeds to work in Discord.

**Deployment on EC2:** Always run `docker compose down` before `docker compose up --build -d` on the `t2.micro` to prevent Maven competing for RAM with running containers, which causes CPU spikes and potential OOM conditions.

### 7.2 Dockerfiles

**Bot (`./Dockerfile`)**

```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["python", "bot/main.py"]
```

**Backend (`./backend/Dockerfile`)** — multi-stage build:

```
Stage 1 (builder): maven:3.9-eclipse-temurin-21
  - mvn dependency:go-offline  (layer-cached)
  - mvn clean package -DskipTests

Stage 2 (runtime): eclipse-temurin:21-jre
  - copies *.jar from builder
  - EXPOSE 8080
  - ENTRYPOINT ["java", "-jar", "app.jar"]
```

The two-stage build means the final image contains only the JRE and the JAR — no Maven or JDK.

### 7.3 Nginx

**`nginx.conf`** runs Nginx as a reverse proxy on port 80 in front of the Spring Boot backend.

**Rate limiting:** `limit_req_zone` at 10 requests/second per IP, with burst of 20 (nodelay). Returns 429 on excess.

**`GET /images/[0-9]+/file`** — public. Proxied to `backend:8080` with rate limiting. No IP restriction. This is the only endpoint accessible from the open internet (Discord crawlers use this to generate embed previews).

**`location /`** — restricted to `172.16.0.0/12` (Docker internal network) and `127.0.0.1`. All external requests are denied with 403. This means only the bot container can call backend API endpoints.

**Client max body size:** 10MB — governs maximum image upload size.

---

## 8. Dependencies

### Bot (`requirements.txt` + runtime imports)

| Package | Purpose |
|---|---|
| `discord.py[voice]` | Discord API client, slash commands, UI components |
| `PyNaCl` | Voice support (required by discord.py voice extra) |
| `aiohttp` | Async HTTP client for backend API calls and attachment downloads |
| `python-dotenv` | `.env` file loading |
| `requests` | Sync HTTP (used only in legacy `art.py`) |
| `bs4` | BeautifulSoup HTML parsing (in requirements, not actively used in current code) |
| `pandas` | In requirements, not actively used in current code |
| `pytz` | Timezone conversion for daily/contest scheduling loops |

### Backend (`pom.xml`)

| Dependency | Purpose |
|---|---|
| `spring-boot-starter-data-jpa` | JPA/Hibernate ORM |
| `spring-boot-starter-web` | REST controllers, embedded Tomcat |
| `spring-boot-starter-security` | Spring Security (via oauth2-client) |
| `spring-boot-starter-oauth2-client` | Future Discord OAuth support |
| `spring-boot-starter-validation` | `@NotNull`, `@Validated` on controllers |
| `spring-boot-starter-actuator` | `/actuator/health` health check endpoint |
| `postgresql` (runtime) | JDBC driver |
| `bucket4j-core` 8.7.0 | Rate limiting (in pom, filter currently commented out) |
| `caffeine` | In-memory cache (in pom, used by commented-out rate limiter) |
| `spring-security-test` (test) | Security test support |

### Frontend (`package.json`)

Early scaffold only. Not production-ready.

| Package | Version |
|---|---|
| `next` | 16.1.6 |
| `react` / `react-dom` | 19.2.3 |
| `tailwindcss` | ^3.4.19 (v3, not v4 — v4 has Windows native binding issues) |
| `typescript` | ^5 |

---

## 9. Environment Variables

### Bot Container

| Variable | Required | Description |
|---|---|---|
| `TOKEN` | Yes | Discord bot token |
| `GUILD_ID` | Yes | Discord guild ID for command syncing |
| `BACKEND_URL` | Yes | e.g. `http://backend:8080` |
| `PUBLIC_URL` | Yes | Public-facing URL for image embeds (e.g. `http://<EC2-IP>`) |
| `API_SERVICE_TOKEN` | Yes | Shared secret for backend authentication |
| `chnl_id` | Legacy | Previously used for hardcoded poem channel; now per-guild from DB |
| `PYTHONPATH` | Yes (Docker) | Set to `/app` in docker-compose |

### Backend Container

| Variable | Required | Description |
|---|---|---|
| `SPRING_DATASOURCE_URL` | Yes | `jdbc:postgresql://db:5432/${POSTGRES_DB}` |
| `SPRING_DATASOURCE_USERNAME` | Yes | Postgres user |
| `SPRING_DATASOURCE_PASSWORD` | Yes | Postgres password |
| `api.service.token` | Yes | Must match bot's `API_SERVICE_TOKEN` |
| `SPRING_JPA_HIBERNATE_DDL_AUTO` | Yes | Currently `update`; planned `validate` after Flyway migration |
| `DISCORD_CLIENT_ID` | Planned | Discord OAuth app client ID |
| `DISCORD_CLIENT_SECRET` | Planned | Discord OAuth app client secret |

### Database Container

| Variable | Required | Description |
|---|---|---|
| `POSTGRES_USER` | Yes | Database user |
| `POSTGRES_PASSWORD` | Yes | Database password |
| `POSTGRES_DB` | Yes | Database name |
| `PORTS` | Yes | Host port mapping (e.g. `5432:5432`) |

---

## 10. Request Flow Walkthroughs

### User runs `/gallery`

```
/gallery
  └─ GET images/all?guildid=X
       └─ GalleryImageRepo.findByGuildidWithVotes()
          (LEFT JOIN votes, GROUP BY image, COUNT — single query)
       └─ returns List<GalleryImageResponse> with voteCount embedded
  └─ group_images_into_posts() — groups by groupId
  └─ renders GalleryViewer (TextDisplay + MediaGallery + nav buttons)

  [◀ or ▶ clicked]
  └─ rebuilds view for new post index — no backend call

  [❤️ clicked]
  └─ POST images/{id}/vote?userID=X
       └─ GalleryImageVoteService.addVote()
          → duplicate: throw InvalidVote → 409
          → new: save GalleryImageVote → 202
  └─ on 409: ephemeral "already voted"
  └─ on 202: increment local voteCount, rebuild view
```

### User runs `/delete`

```
/delete
  └─ GET images/user/{userId}?guildid=X
       └─ GalleryImageRepo.findByUploaderIDAndGuildid()
       └─ returns user's submissions for that guild
  └─ renders DeleteView (Select menu, up to 25 options, 60s timeout)

  [User selects a submission]
  └─ DELETE images/{id}
       └─ GalleryImageService.deleteImage()
          → GalleryImageRepo.delete() — cascades to votes (CascadeType.ALL)
       └─ 204: edit message to "Submission deleted!"
       └─ non-204: edit message to "Failed to delete."
```

### User runs `/upload` with two images

```
Discord
  └─ slash command interaction → bot/commands/gallery.py upload()
       └─ defer(ephemeral=True, thinking=True)
       └─ validate content_type of both attachments
       └─ aiohttp.ClientSession: download both attachment bytes
       └─ build aiohttp.FormData with two "files" fields + uploaderid + guildid + title
       └─ api.post("images/add-multiple", data=form)
            └─ aiohttp sends POST http://backend:8080/images/add-multiple
                 └─ [Docker DNS resolves "backend"]
                 └─ Nginx (port 80) — bot is on internal network, skips IP deny
                 └─ Spring Boot receives request
                      └─ ServiceTokenFilter validates Bearer token → sets ROLE_BOT
                      └─ GalleryImageController.addImages()
                           └─ GalleryImageService.addImages()
                                └─ generates one shared groupId UUID
                                └─ saves GalleryImage #1 (with groupId)
                                └─ saves GalleryImage #2 (with groupId)
                                └─ returns List<GalleryImageResponse>
                      └─ 201 Created
  └─ bot receives 201, sends ephemeral "Your 2 images have been added!"
```

### Daily poem fires for a guild

```
bot/commands/daily.py _poem_loop (background asyncio.Task)
  └─ api.get("guilds/with-poems")
       └─ GET http://backend:8080/guilds/with-poems
            └─ GuildSettingsController.getGuildsWithPoems()
            └─ returns List<GuildSettingsResponse> where poemChannelId is not null
  └─ for each guild: compute _next_daily(hour, minute, tz)
  └─ discord.utils.sleep_until(next_time)
  └─ [time fires]
  └─ scrape() → GET https://poetrydb.org/linecount/15 → random poem
  └─ bot.get_channel(poemChannelId)
  └─ channel.send("@everyone", embed=poem_embed)
  └─ loop back to top
```

### Contest winner announcement

```
bot/commands/contest.py _contest_loop
  └─ end event fires for guild X
  └─ announce_winner(guild)
       └─ api.get("/images/contest/winner", params={"guildid": guild_id})
            └─ GET http://backend:8080/images/contest/winner?guildid=X
                 └─ GalleryImageController.getContestWinner()
                      └─ GalleryImageService.getContestWinner()
                           └─ GalleryImageVoteService.getWinningImage(guildId)
                                └─ findWinningImagesByGuild(guildId, PageRequest.of(0, 1))
                                   (GROUP BY image ORDER BY COUNT(vote) DESC LIMIT 1)
                           └─ returns ContestWinner{id, uploaderid, votes}
       └─ build embed with winner info + image URL
       └─ channel.send(embed=embed)
```

---

## 11. Pending Work & Known TODOs

### Contest Signup Flow (not yet implemented)

The contest announcement view has a disabled `"signup"` button. The full flow requires:

- New `ContestSignups` entity + `ContestSignupRepo` + `ContestSignupService` + `ContestController`
- Rules: one signup per user per guild, verified users only, signups blocked after contest deadline
- Bot-side: button handler that checks Discord verification status and calls the signup endpoint, handling 403 (unverified), 404 (guild not configured), 409 (duplicate or closed)

### Poem / PoemVote Models

`Poem.java` and `PoemVote.java` exist as JPA entities with repositories (`PoemRepo`, `PoemVoteRepo`) but no controller, service, or bot command is wired to them. The intended feature is a community poem submission system.

### Frontend

The Next.js app in `frontend/` is a default scaffold with no feature code. Planned features: gallery browsing, Discord OAuth login via `spring-boot-starter-oauth2-client` on the backend.

### Open Security Gap

Port 8080 on the EC2 security group is open. The backend should only be reachable through Nginx on port 80. Port 8080 should be closed in the AWS security group.

### `chnl_id` Env Variable

The `bot/config.py` loaded `CHANNEL_ID = int(os.getenv("chnl_id"))` in the old version. The current `daily.py` no longer uses this — it fetches guild-specific channel IDs from the database. This env var is no longer needed and can be removed from `config.py` and `docker-compose.yml`.

---

*Documentation generated from codebase review — April 2026*
