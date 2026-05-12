# Sprint 1 Retro

## What Went Well + Celebrate

- Diego completed the CI workflow and pushed the code, which ensured the tests will run on each push and pull request.
- Dana wrote the tests in a timely manner so that the team could continue with implementation.

## What Could Be Improved?

- Make sprint todos more manageable and reflective of current progress instead of listing work that is too far ahead before the groundwork is built.
- Use structured and mandatory due dates so the team is not held back by a single implementation.
- Improve communication and contribution from all team members for their respective parts.

## Which Improvements Will the Team Commit to in Sprint 2?

- Create clearer and more achievable Sprint 2 Kanban cards.
- In each lab section, go over what was completed that week to keep the team accountable for finishing necessary tasks.
- Write user stories in Kanban cards so the team stays focused on real human pain points.

## AI Tools Reflection

Cursor and Claude made Sprint 1 faster when we needed to turn working bot code into repeatable checks. Instead of hand-writing every pytest case from scratch, we used AI to draft the tests in `unittests/test_bot_runtime_config_and_sync.py` and `unittests/test_discord_voice_runtime_adapter.py`, then tightened them so they matched our code. AI also helped us get to a working CI workflow faster by drafting the GitHub Actions structure in `.github/workflows/ci.yml`, including checkout, Python 3.11 setup, running `pytest unittests`, and wiring `ELEVENLABS_API_KEY` through GitHub Actions secrets instead of hard-coding anything.

The harder part was that AI-generated code looked plausible before it was actually correct, so we still had to do a lot of verification. Some suggestions were too generic for our repo and missed project-specific details, like making the tests import from `apps.bot` correctly, and avoiding a hard dependency on `discord.py` inside the config/sync tests. The same thing happened with CI: AI could scaffold the workflow quickly, but getting from "reasonable YAML" to a workflow that actually passed took manual debugging of environment variables, dependency assumptions, and test paths. In practice, AI was best at accelerating boilerplate and first drafts; it was worse when we treated its output as final instead of as something that still needed careful review. 

## Sprint 2 Commitments

- https://github.com/orgs/CSEN-SCU/projects/4/views/1?pane=issue&itemId=186839589&issue=CSEN-SCU%7Ccsen-174-s26-team-project-ttstt%7C21

- https://github.com/orgs/CSEN-SCU/projects/4/views/1?pane=issue&itemId=186853994&issue=CSEN-SCU%7Ccsen-174-s26-team-project-ttstt%7C22

