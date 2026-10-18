# Autonomous development loop setup

This workflow is a guarded coding-agent runner, not just a build monitor. When enabled, it resumes a persistent branch, reads issue #2 and the latest failed Android build logs, asks an OpenAI-compatible coding model to make one bounded change, runs the existing JavaScript regression tests, retries a failed validation once, pushes only to a candidate branch, triggers an APK build, and opens/updates a **draft** pull request. It never merges to `main`.

## Required repository configuration

The runner is deliberately disabled until the repository owner configures a model provider; this avoids silently consuming API quota or money.

In GitHub repository **Settings → Secrets and variables → Actions**:

1. Add secret `AI_API_KEY` containing a key for the chosen OpenAI-compatible provider.
2. Add variable `AI_API_BASE` containing that provider's API base URL.
3. Add variable `AI_MODEL` containing the exact model identifier expected by the provider (without an `openai/` prefix).
4. Add variable `AUTONOMOUS_AGENT_ENABLED` with value `true` to enable scheduled execution.

Choose a provider and model only after checking its current free-tier limits, rate limits, data terms, and pricing. This repository does not supply a model key, and the workflow cannot guarantee that a third-party endpoint is free. Never put keys in repository files or variables; use the secret field.

## Run behavior and safety limits

- Scheduled cadence: every 30 minutes; manual trigger is also available.
- Each invocation has a 25-minute hard timeout and makes at most two edit/validation attempts.
- Existing branch `autonomous/mnn-diffusion` is resumed across runs.
- Validation extracts the Android ZIP, applies the patch script, and runs both JavaScript regression suites.
- After a successful candidate change, the workflow triggers `mobile-apk-build.yml` and opens or updates a draft PR.
- Android APK build success is not proof of on-device diffusion inference. MNN/model integration still requires actual inference evidence and license review.
- The agent is not allowed to merge the PR automatically. Review the diff and CI artifacts before merging.
- If the provider configuration is missing, no agent job runs while the enable flag is false. If enabled with missing credentials, the run fails early with a clear configuration error.

## Important limitations

GitHub Actions jobs are finite runs, not a permanently running process. Progress is made in repeated bounded cycles and persisted through the candidate branch and PR. The agent requires an API key and provider endpoint; this workflow does not provision a model service or purchase compute.
