# Bot And Backend Test Suite Spec

## Goals

- Make bot/backend behavior testable without live Discord, backend, museum, poem, or database calls.
- Cover the contracts that connect the Python bot to the Spring Boot API: auth headers, request paths, status handling, upload/vote/delete flows, and response shape.
- Keep tests focused by layer: pure Python unit tests for bot helpers, mocked interaction tests for bot command behavior, Java unit tests for services/filters, and Spring MVC slices for endpoint contracts.

## Current State

- Python has `tests/test_scraper.py`, which exercises poem scraping and depends on external content.
- Backend has Mockito service tests for guild setup, contest signups, and contest winner selection.
- No tests currently cover the bot API helper, gallery grouping logic, backend service-token filter, gallery add/delete/vote service edges, or controller request/response contracts.
- `RateLimitFilter.java` is commented out and is excluded from implementation coverage until it becomes live code.

## Suite Layers

### Bot Unit Tests

- `bot.apihelper.api`
  - Creates and reuses an `aiohttp.ClientSession`.
  - Sends the bearer `Authorization` header from `API_SERVICE_TOKEN`.
  - Normalizes leading slashes in helper paths.
  - Returns JSON for successful `GET` calls and `None` for non-200 responses.
  - Returns `(status, text)` for `POST` and `DELETE`.
  - Closes and clears the shared session on shutdown.
- `bot.commands.gallery`
  - Groups flat image lists into stable post groups by `groupId`.
  - Falls back to image id for ungrouped images.
  - Keeps input ordering so pagination is predictable.

### Bot Command Tests

- Gallery browser
  - Empty gallery sends the empty-state response.
  - Non-empty gallery creates a `GalleryViewer` with grouped posts.
  - Vote handles duplicate vote `409` separately from a successful vote.
- Upload
  - Rejects non-image attachments before network download.
  - Uses `/images/add` for one file and `/images/add-multiple` for grouped uploads.
  - Includes uploader, guild, title, and command/user headers.
- Delete
  - Empty user submissions send an empty-state response.
  - Populates at most 25 select options.
  - Successful delete edits the message and clears the view.

### Backend Unit Tests

- `ServiceTokenFilter`
  - Skips `/actuator/health`.
  - Skips `GET /images/{id}/file`.
  - Rejects missing, malformed, and wrong bearer tokens with `401` JSON.
  - Authenticates valid bot tokens with `ROLE_BOT`, invokes the chain, then clears the security context.
- `GalleryImageService`
  - Single upload defaults missing titles to `Untitled`.
  - Multi-upload assigns one shared group id to all images in a batch.
  - `getImagesByUploader` maps repository images with vote counts.
  - `vote` delegates to `GalleryImageVoteService` after loading the image.
  - `deleteImage` deletes the loaded image and returns `404` when missing.
- `GalleryImageVoteService`
  - Duplicate votes raise `InvalidVote`.
  - New votes save a `GalleryImageVote`.
  - Vote counts delegate to the repository.

### Backend Controller Tests

- `GalleryImageController`
  - Multipart single and multi upload return `201` and `Location`.
  - Vote returns `202`.
  - Delete returns `204`.
  - Missing required params return structured `VALIDATION_ERROR`.
- `GuildSettingsController`
  - Setup endpoints bind request params into DTOs.
  - Delete endpoints return `204`.
- `ContestController`
  - Signup, withdraw, and list endpoints delegate with expected request params.
- `GlobalExceptionHandler`
  - `InvalidVote` maps to `409 INVALID_VOTE`.
  - `ResponseStatusException` maps to `REQUEST_ERROR`.
  - Unexpected exceptions map to `500 INTERNAL_ERROR`.

## Implementation Tasks

1. Add this spec document and use it as the coverage checklist.
2. Add stable bot unit tests for `bot.apihelper.api`.
3. Add stable bot unit tests for gallery grouping.
4. Add backend unit tests for `ServiceTokenFilter`.
5. Add backend unit tests for `GalleryImageService` upload, grouping, vote, and delete edges.
6. Add backend unit tests for `GalleryImageVoteService`.
7. Run Python and backend test suites.
8. Commit only the spec and test-suite changes, push the testing branch, and open a draft PR into `main`.

## Follow-On Tasks

- Replace or isolate live poem scraper tests with mocked HTML fixtures.
- Add mocked Discord interaction tests for gallery, upload, and delete commands.
- Add Spring MVC controller slice tests for request binding, validation errors, and response status contracts.
- Add persistence tests for JPA mappings once an in-memory or Testcontainers database strategy is chosen.
