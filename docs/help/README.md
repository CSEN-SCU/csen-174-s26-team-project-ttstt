# TTSTT public help site

Static help guide hosted on **Netlify** for the `/help` Discord slash command.

## Public URL

Copy the URL from your Netlify site dashboard (e.g. `https://your-site-name.netlify.app/`) and set it as `HELP_URL` in the bot `.env` (see [`apps/bot/.env.example`](../../apps/bot/.env.example)).

## Deploy on Netlify (Git-connected)

This repo includes [`netlify.toml`](../../netlify.toml) at the root so Netlify publishes `docs/help/` automatically—no build step.

1. [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import an existing project** → GitHub → this repo.
2. Netlify should detect `netlify.toml` and set **Publish directory** to `docs/help`. If not, set it manually.
3. **Deploy site**, then copy the live URL into `HELP_URL` on the bot host and restart the bot.

Pushes to the connected branch trigger new deploys.

## Manual upload (optional)

[app.netlify.com/drop](https://app.netlify.com/drop) → drag this `docs/help` folder. Re-upload after HTML/CSS changes.

## Verify the deploy

1. In Netlify: **Deploys** → latest deploy should be **Published**.
2. Open the site URL in a browser; you should see **TTSTT Help** and the command tables.
3. Confirm `styles.css` loads (page is styled, not plain unstyled HTML).
4. Set the same URL in bot `.env` as `HELP_URL` and run `/help` in Discord.

## Local preview

```bash
cd docs/help
python -m http.server 8080
```

Then visit http://localhost:8080/
