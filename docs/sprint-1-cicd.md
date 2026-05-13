# Sprint 1 — CI/CD

## Merged PR with Passing CI check
https://github.com/CSEN-SCU/csen-174-s26-team-project-ttstt/actions/runs/25405659911

## Platform choice

The team’s **product platform is Discord**. TTSTT is a Discord bot that must run where users already coordinate voice and text, so **discord.py** and the Discord gateway are the stack anchor rather than a separate web or desktop client for this sprint. Discord fits the project because it exposes voice channels, text channels, and permissions in one place, and the OAuth invite flow lets teammates add the bot to real guilds for integration testing (see the live authorize URL below). **GitHub Actions** is only where we run automated checks on pushes and pull requests; it complements Discord but is not the surface we chose for users. The first integration pass that tripped us up was **aligning the Developer Portal with our code**: the bot enables `guilds`, `voice_states`, and `message_content` in `main.py`, but Discord will not deliver those events until the same intents are turned on under the application’s **Bot** and **Privileged Gateway Intents** settings, which otherwise looks like a bot that connects yet never “hears” voice or chat.

## Secrets handling

The team keeps API credentials out of source control and configures them only in GitHub (**Settings → Secrets and variables → Actions**). Right now the repository defines a single secret, **`ELEVENLABS_API_KEY`**, which is required for ElevenLabs TTS calls when implementations or integration tests eventually need live access. CI reads that value at workflow runtime via the **`${{ secrets.ELEVENLABS_API_KEY }}`** expression on the **`test`** job’s `env:` block, which exposes it as the shell environment variable `ELEVENLABS_API_KEY` for subsequent steps without ever printing or committing the key. When we deploy the bot or API beyond GitHub Actions, the same credential will need to be set on whatever deployment surface we choose (hosted env vars, vault, or `.env` on the host—never checked in); we will mirror the same variable name there for consistency unless the provider requires a different convention. As we add services (for example Postgres or Discord tokens), we will document each secret, whether it belongs to CI-only, deployment-only, or both, and wire them through the same pattern rather than embedding values in workflows or application code.

Live URL: https://discord.com/oauth2/authorize?client_id=1496265708215075016
Screenshot: ![Deploy dashboard](images/deploy.png)