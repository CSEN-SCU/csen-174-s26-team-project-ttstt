# Infrastructure

Optional **Postgres** for future backend development (no application code in-repo yet).

```bash
cd infra
docker compose up -d
```

- **Postgres:** `localhost:5432`, user/password/database `app` / `app` / `app` (development defaults only).

Stop: `docker compose down` (add `-v` to remove the Postgres volume).

When implemented, the API and Discord bot will run outside this compose file; voice traffic uses **Discord’s** infrastructure.
