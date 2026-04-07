# Infrastructure

```bash
cd infra
docker compose up -d
```

- **Murmur:** TCP/UDP `64738` — use this as the Mumble server when running `apps/web`.
- **Postgres:** `localhost:5432`, user/password/db `app` / `app` / `app` (dev only).

Stop: `docker compose down` (add `-v` to drop the Postgres volume).
