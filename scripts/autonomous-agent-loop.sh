#!/usr/bin/env bash
set -euo pipefail

: "${AI_API_KEY:?AI_API_KEY is required}"
: "${AI_API_BASE:?AI_API_BASE is required}"
: "${AI_MODEL:?AI_MODEL is required}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

ISSUE_JSON="$(gh issue view 2 --repo "$GITHUB_REPOSITORY" --json title,body)"
ISSUE_TITLE="$(python -c 'import json,sys; print(json.load(sys.stdin)["title"])' <<<"$ISSUE_JSON")"
ISSUE_BODY="$(python -c 'import json,sys; print(json.load(sys.stdin)["body"])' <<<"$ISSUE_JSON")"

# Pull the latest failed Android CI log, if one exists, so the next cycle can
# diagnose a real failure instead of repeating the same blind change.
FAILED_RUN="$(gh run list --repo "$GITHUB_REPOSITORY" --workflow mobile-apk-build.yml \
  --branch autonomous/mnn-diffusion --limit 5 --json databaseId,conclusion \
  --jq '[.[] | select(.conclusion == "failure")][0].databaseId // empty' 2>/dev/null || true)"
CI_CONTEXT="No recent failed Android build was found for the agent branch."
if [[ -n "$FAILED_RUN" ]]; then
  gh run view "$FAILED_RUN" --repo "$GITHUB_REPOSITORY" --log-failed > "$WORK_DIR/failed-ci.log" 2>&1 || true
  # Bound prompt size; keep the tail where the actionable compiler/test errors usually are.
  tail -c 18000 "$WORK_DIR/failed-ci.log" > "$WORK_DIR/failed-ci-tail.log"
  CI_CONTEXT="Latest failed Android workflow run: $FAILED_RUN. Failure log tail:\n$(cat "$WORK_DIR/failed-ci-tail.log")"
fi

cat > "$WORK_DIR/task.md" <<'PROMPT'
You are the coding agent for AI Comic Studio. Make one bounded, real implementation improvement per run.
The product goal is Android-first comic creation with optional true on-device image generation, no mandatory paid image API, and honest status reporting.

Rules:
- Inspect the existing repository before editing; continue from the current branch, do not reset or overwrite prior work.
- Focus on a small, testable implementation step toward the MNN Diffusion Android integration described in the issue below.
- Prefer working code and regression tests over planning documents or UI-only changes.
- The Android project is packaged as a ZIP and patched by scripts/patch-comic-studio.py. Do not claim to have changed the ZIP's binary contents.
- Do not claim local inference works unless the repository contains an actual native integration and an inference result is verified.
- Preserve existing features. Do not remove tests, weaken assertions, skip validation, or disguise mocked tests as real inference.
- Do not edit workflow permissions, secrets, credentials, or this autonomous runner. Never print or read secrets.
- Do not add paid API dependencies, model weights, or large binary files. Do not download/commit model weights.
- Avoid speculative dependencies. Check official MNN integration details if network access is available; otherwise state uncertainty in code comments/docs.
- Make changes only to tracked source/test/documentation files. Do not modify binary ZIPs or generated build outputs.
- If the best next step is blocked by missing Android/NDK context, implement a concrete preparatory test or compatibility check rather than pretending integration is done.
- Keep the change small enough to review. Run the supplied validation commands after editing.
PROMPT

cat >> "$WORK_DIR/task.md" <<EOF

## GitHub issue #2: $ISSUE_TITLE

$ISSUE_BODY

## Latest Android CI context

$CI_CONTEXT

## Required outcome this run

Inspect the current code, identify the highest-value bounded next step, implement it, and explain exactly what changed and what remains unverified. Do not merely restate the issue.
EOF

run_validation() {
  set -euo pipefail
  ZIP_FILE="$(find . -maxdepth 1 -type f -iname '*.zip' -print -quit)"
  test -n "$ZIP_FILE" || { echo "Validation failed: Android project ZIP not found."; return 1; }
  rm -rf "$WORK_DIR/extracted"
  mkdir -p "$WORK_DIR/extracted"
  unzip -q "$ZIP_FILE" -d "$WORK_DIR/extracted"
  PROJECT_DIR="$(find "$WORK_DIR/extracted" -type f \( -name settings.gradle -o -name settings.gradle.kts \) -print -quit | xargs -r dirname)"
  test -n "$PROJECT_DIR" || { echo "Validation failed: Gradle settings not found."; return 1; }
  test -d "$PROJECT_DIR/app" || { echo "Validation failed: app module not found."; return 1; }
  if [[ -d android-overlay ]]; then cp -a android-overlay/. "$PROJECT_DIR"/; fi
  python3 scripts/patch-comic-studio.py "$PROJECT_DIR"
  node scripts/test-webapp.cjs "$PROJECT_DIR/app/src/main/assets/index.html"
  node scripts/test-comic-studio.cjs "$PROJECT_DIR/app/src/main/assets/index.html"
}

for attempt in 1 2; do
  echo "=== Autonomous implementation attempt $attempt/2 ==="
  aider --model "openai/$AI_MODEL" --no-auto-commits --yes-always \
    --file scripts/patch-comic-studio.py \
    --file scripts/test-comic-studio.cjs \
    --file scripts/test-webapp.cjs \
    --file README.md \
    --file THIRD_PARTY_NOTICES.md \
    --message-file "$WORK_DIR/task.md"

  if run_validation > "$WORK_DIR/validation.log" 2>&1; then
    cat "$WORK_DIR/validation.log"
    echo "PASS: source patching and JavaScript regression tests passed."
    exit 0
  fi

  echo "Validation failed on attempt $attempt:"
  tail -c 12000 "$WORK_DIR/validation.log" || true
  if [[ "$attempt" -eq 1 ]]; then
    {
      printf '\n\n## Validation failure after the first edit attempt\n'
      tail -c 12000 "$WORK_DIR/validation.log"
      printf '\nFix this concrete failure without weakening the tests, then rerun validation.\n'
    } >> "$WORK_DIR/task.md"
  fi
done

echo "::error::Autonomous edit loop exhausted its two validation attempts."
exit 1
