# On-device image generation: current integration status

## What this change provides

- The Android host exposes `AndroidDiffusion.getStatusJson()` to the WebView.
- The diagnostics panel reports the presence of known native-library filenames and inventories files in the app-private `files/models/mnn-diffusion` directory.
- The UI explicitly reports `inferenceAvailable: false`. Finding a library or model file is not proof of working image generation.

## What is not integrated yet

- No MNN native runtime is built or packaged by this project.
- No compatible JNI inference entry point is wired to the comic editor.
- No model download, integrity manifest, conversion pipeline, or license-verified model package is supplied.
- The upstream MNN Android app's `mnnllmapp` library and `DiffusionSession` are examples, not a drop-in binary dependency for this app.

## Requirements before enabling generation

1. Pin a reviewed MNN source revision and build the required Android ABIs with the NDK/CMake toolchain.
2. Implement an app-specific JNI wrapper with deterministic create/generate/cancel/release behavior and progress/error reporting.
3. Specify and validate the exact converted model directory layout; keep model weights out of the APK and Git.
4. Add resumable model downloads, SHA-256 verification, free-space checks, cancellation/retry, and clear licensing/source attribution.
5. Connect the editor's per-panel prompt to native inference on a background executor.
6. Add instrumentation or device-run evidence that creates and opens an actual generated image offline. A successful APK build alone is insufficient.

Official upstream reference: https://github.com/alibaba/MNN/tree/master/apps/Android/MnnLlmChat
