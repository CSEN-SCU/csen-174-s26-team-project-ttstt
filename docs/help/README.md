# TTSTT public help site

Static help guide deployed to GitHub Pages for the `/help` Discord slash command.

## Public URL

After the first successful deploy on `main`:

**https://csen-scu.github.io/csen-174-s26-team-project-ttstt/**

Set the same value as `HELP_URL` in the bot environment (see [`apps/bot/.env.example`](../../apps/bot/.env.example)).

## One-time GitHub setup

1. Repo **Settings → Pages**
2. **Build and deployment → Source:** GitHub Actions
3. Merge to `main` (or run the **Deploy help site** workflow manually)

The workflow [`.github/workflows/pages.yml`](../../.github/workflows/pages.yml) publishes everything under `docs/help/`.

## Local preview

Open `index.html` in a browser, or serve the folder:

```bash
cd docs/help
python -m http.server 8080
```

Then visit http://localhost:8080/
