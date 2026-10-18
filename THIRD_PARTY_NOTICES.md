# THIRD_PARTY_NOTICES — AI Comic Studio

This file is a working register. It is not a claim that all dependencies or assets have already been audited. Before a commercial release, populate exact versions and licenses from the built Android project's dependency report and inspect all bundled assets.

## Application code

The repository contains project-specific code and a patch script used to inject the Comic Studio UI into the Android project's HTML asset. Confirm the rights and intended license for each project-specific file before selecting a distribution license for the overall application.

## Known development/build components

| Component | Current role | License/terms | Distribution note |
|---|---|---|---|
| Android SDK / build tools | Build the Android APK in CI | See Google's current legal terms | Do not imply Google endorses the app or misuse Android trademarks |
| Gradle | Build system | Check the exact distribution/version terms | Build-time tool; verify whether any Gradle components are bundled at runtime |
| GitHub Actions | CI execution | GitHub service terms and each action's license/terms | Build-time service, not an app runtime dependency |
| reactivecircus/android-emulator-runner | CI emulator test action | Verify upstream license and pinned revision before release pipeline reliance | CI-only action |
| ComfyUI | Optional separate local inference server; not assumed bundled in APK | GPL-3.0 upstream | If distributed, modified, or packaged with the product, review GPL obligations and provide required notices/source under the applicable terms |
| Image-generation model weights | Not yet selected as a bundled model | Must be checked per exact model/version | Do not redistribute or advertise commercial use until the exact license has been reviewed |
| Language model weights | Not yet selected as a bundled model | Must be checked per exact model/version | Same requirement |
| ComfyUI custom nodes / Python packages | Not yet selected as a bundled set | Must be checked package-by-package | Record transitive dependencies and any attribution obligations |

## Known upstream license source

- ComfyUI GPL-3.0: https://github.com/Comfy-Org/ComfyUI/blob/master/LICENSE

## Release gate — must complete before commercial distribution

- [ ] Record all direct and transitive Gradle dependencies with exact versions.
- [ ] Audit every file in the source ZIP, including fonts, images, audio, icons, sample content and web assets.
- [ ] Generate an SBOM or equivalent dependency inventory.
- [ ] Add exact license texts and required copyright/attribution notices for each included component.
- [ ] Record the exact model files, hashes, download sources and license terms.
- [ ] Record custom nodes, Python packages, model auxiliaries and workflow licenses.
- [ ] Confirm rights to the app name, logo, product artwork and all demonstration materials.
- [ ] Have the final distribution plan reviewed for the jurisdictions and stores where the product will be sold.

**Do not treat an empty or incomplete entry as permission to use a component commercially.**