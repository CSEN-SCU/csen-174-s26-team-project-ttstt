# TTSTT public help site

Static help guide hosted on **Netlify** for the `/help` Discord slash command.

## Public URL

Use the URL from your Netlify site dashboard (e.g. `https://your-site-name.netlify.app/`).

Set that exact URL as `HELP_URL` in the bot environment (see [`apps/bot/.env.example`](../../apps/bot/.env.example)).

## Deploy on Netlify

### Option A — Connect this GitHub repo (recommended)

1. Sign in at [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import an existing project** → GitHub → select this repo.
2. Build settings:
   - **Base directory:** `docs/help` (if Netlify asks for the folder that contains `index.html`)
   - **Build command:** leave empty
   - **Publish directory:** `.` (when base is `docs/help`) or `docs/help` (if base is repo root)
3. **Deploy site**. Copy the generated URL and set `HELP_URL` on the bot host.

Pushes to the connected branch redeploy automatically.

### Option B — Manual upload (no Git hookup)

1. Open [app.netlify.com/drop](https://app.netlify.com/drop).
2. Drag this `docs/help` folder onto the page.
3. Use the URL Netlify gives you for `HELP_URL`.

Re-upload after you change `index.html` or `styles.css`.

## Local preview

```bash
cd docs/help
python -m http.server 8080
```

Then visit http://localhost:8080/

## Note on GitHub Pages

The workflow [`.github/workflows/pages.yml`](../../.github/workflows/pages.yml) is optional and only needed if the org enables GitHub Pages later. Netlify is the supported host for this site.
