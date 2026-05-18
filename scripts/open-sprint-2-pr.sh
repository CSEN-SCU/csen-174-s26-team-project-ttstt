#!/usr/bin/env bash
# Push sprint-2-red-team-remediations and open a PR into main.
# Run from repo root: ./scripts/open-sprint-2-pr.sh

set -euo pipefail
cd "$(dirname "$0")/.."

git checkout sprint-2-red-team-remediations

echo "Pushing branch sprint-2-red-team-remediations..."
git push -u origin sprint-2-red-team-remediations

PR_URL=$(gh pr create \
  --base main \
  --head sprint-2-red-team-remediations \
  --title "Sprint 2: remediate peer red-team findings 2.2 and 3.1" \
  --body "$(cat <<'EOF'
## Summary

Addresses SmartShop peer red-team findings for TTSTT (May 12, 2026):

- **Finding 2.2** (AI API security): Unmoderated transcript relay — harmful content posted verbatim
- **Finding 3.1** (Responsible AI): Sensitive voice disclosures relayed publicly without safeguard

## Changes

- Add `apps/bot/content_moderation.py` with URL redaction, keyword-based sensitive-content detection, optional OpenAI Moderation API
- Wire STT through `moderate_for_transcript()` in `apps/bot/stt.py` (DM for sensitive speech, 988 crisis line for self-harm)
- Wire TTS through `moderate_for_tts()` in `apps/bot/main.py`
- Privacy notice on `/join`; document in `apps/bot/README.md`
- Add `docs/red-team-report-ttstt-received.md`, `docs/sprint-2-remediations.md`, `unittests/test_content_moderation.py`

## Test plan

- [ ] `python -m pytest -q unittests/test_content_moderation.py`
- [ ] `python -m pytest -q unittests`
- [ ] After merge, update merged PR URLs in `docs/sprint-2-remediations.md`

EOF
)")

echo ""
echo "PR created: $PR_URL"
echo "After merging, paste this URL into docs/sprint-2-remediations.md (both Merged PR rows)."
