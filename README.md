# Mumble assistant (voice chat + Whisper STT + Piper TTS)

Full-stack project around **Mumble** (voice), a **web client** fork, and a **Python API** for speech and user preferences — structured for CSEN 174-style delivery (tests, CI, deploy, ADRs).

## Layout

| Path | Purpose |
|------|---------|
| [`apps/web`](apps/web) | Mumble web client (fork of mumble-web) — UI + connection to Murmur + your API |
| [`apps/api`](apps/api) | FastAPI backend — Whisper STT, Piper TTS, auth, DB (to be expanded) |
| [`vendor/mumble`](vendor/mumble) | Upstream **Mumble desktop** source — reference only; not part of CI/build |
| [`infra`](infra) | `docker-compose` for Murmur + Postgres (local dev) |
| [`docs`](docs) | Journal, syllabus notes, ADRs |

## Quick start

1. **Voice server + DB:** see [`infra/README.md`](infra/README.md).
2. **API:** see [`apps/api/README.md`](apps/api/README.md).
3. **Web client:** see [`apps/web/README.md`](apps/web/README.md) (install deps, `npm run build` / dev server per upstream docs).

## Nested Git repositories

`apps/web` and `vendor/mumble` may still contain their own `.git` directories from the original clones. To make this workspace a **single** team repo, remove those nested `.git` folders and `git add` everything from the workspace root (or convert them to [submodules](https://git-scm.com/docs/git-submodule)).

## Syllabus

Course HTML is at the repo root: `CSEN 174_ Software Engineering _ Spring 2026 _ Santa Clara University.html`.
