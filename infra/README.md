# Infrastructure

Local **Postgres** for the deployable Discord bot in `apps/bot`.

```bash
cd infra
docker compose up -d
```

- **Postgres:** `localhost:5432`, user/password/database `app` / `app` / `app` (development defaults only).

Stop: `docker compose down` (add `-v` to remove the Postgres volume).

Initialize bot schema after Postgres starts:

```bash
cat ../apps/bot/sql/voice_preferences.sql | docker compose exec -T postgres psql -U app -d app
```

The bot itself runs outside this compose file (`python -m apps.bot.main`); voice traffic still uses Discord infrastructure.
