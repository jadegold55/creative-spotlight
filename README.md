# Creative Spotlight

Creative Spotlight is a Discord community project that blends art sharing, poetry discovery, and weekly spotlight contests.

The repository includes:
- A **Python Discord bot** for slash commands and interactive gallery voting.
- A **Spring Boot backend** for persisting gallery images and votes.
- A **PostgreSQL database** for storage.

## Features

### Discord bot commands
- `/gallery` — browse uploaded images in an interactive viewer and vote with a ❤️ button.
- `/upload` — submit an image URL or attachment to the gallery.
- `/poem` — fetch a random poem (optionally filtered by author/title).

### Weekly spotlight contest
- A scheduled task announces a weekly art contest in a configured spotlight channel.
- After 7 days, the bot fetches the winning image from the backend and posts the winner.

## Project structure

```text
.
├── bot/                      # Python Discord bot
│   ├── commands/             # Slash command cogs
│   ├── scraping/             # Poem scraping utilities
│   └── main.py               # Bot entrypoint
├── backend/                  # Spring Boot REST API
│   └── src/main/java/...     # Controllers, services, repositories, models
├── tests/                    # Python tests
├── docker-compose.yml        # Local multi-service orchestration
└── Dockerfile                # Bot container image
```

## Requirements

### Local development
- Python 3.10+
- Java 17+
- Maven 3.9+ (or use `backend/mvnw`)
- PostgreSQL 16+

### Containerized development
- Docker
- Docker Compose
