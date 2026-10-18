# Android source overlay

Files placed here are copied over the extracted Android Gradle project before the Comic Studio HTML patch and before CI builds the APK.

Use the same relative paths as the Android project root. For example:
- `android-overlay/app/src/main/java/<package>/...` becomes `<project>/app/src/main/java/<package>/...`
- `android-overlay/app/src/main/cpp/...` becomes `<project>/app/src/main/cpp/...`

This overlay exists because the upstream Android project is currently stored in a ZIP; editing extracted files alone would be lost on the next CI run. Keep changes small, reviewable, and covered by build-time checks. Do not place model weights or secrets here. Native code/library compilation is not proof of image inference: an actual model run and returned image are required for acceptance.
