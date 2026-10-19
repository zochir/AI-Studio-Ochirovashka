#include <jni.h>
#include <string>
#include <exception>
#include <diffusion/diffusion.hpp>

using MNN::DIFFUSION::Diffusion;
using MNN::DIFFUSION::STABLE_DIFFUSION_1_5;

static std::string fromJava(JNIEnv* env, jstring value) {
    if (!value) return {};
    const char* chars = env->GetStringUTFChars(value, nullptr);
    if (!chars) return {};
    std::string result(chars);
    env->ReleaseStringUTFChars(value, chars);
    return result;
}

extern "C" JNIEXPORT jlong JNICALL
Java_com_ainewsstudio_app_AndroidDiffusionBridge_nativeCreate(
    JNIEnv* env, jobject, jstring modelPath) {
    try {
        const std::string path = fromJava(env, modelPath);
        if (path.empty()) return 0;

        // Prefer the mobile GPU backend, but retry with CPU on devices where OpenCL
        // is unavailable or cannot initialize. A CPU fallback may be slower, but it
        // avoids treating GPU support as a hard requirement for local generation.
        const MNNForwardType backends[] = {MNN_FORWARD_OPENCL, MNN_FORWARD_CPU};
        for (const auto backend : backends) {
            Diffusion* diffusion = nullptr;
            try {
                diffusion = Diffusion::createDiffusion(
                    path, STABLE_DIFFUSION_1_5, backend, 0);
                if (diffusion && diffusion->load()) {
                    return reinterpret_cast<jlong>(diffusion);
                }
            } catch (...) {
                // Try the next backend after releasing any partially initialized instance.
            }
            delete diffusion;
        }
        return 0;
    } catch (...) {
        return 0;
    }
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_ainewsstudio_app_AndroidDiffusionBridge_nativeGenerate(
    JNIEnv* env, jobject, jlong handle, jstring prompt,
    jstring outputPath, jint steps, jint seed) {
    auto* diffusion = reinterpret_cast<Diffusion*>(handle);
    if (!diffusion) return JNI_FALSE;
    try {
        const std::string promptText = fromJava(env, prompt);
        const std::string output = fromJava(env, outputPath);
        if (promptText.empty() || output.empty() || steps <= 0) return JNI_FALSE;
        return diffusion->run(promptText, output, steps, seed, {}) ? JNI_TRUE : JNI_FALSE;
    } catch (...) {
        return JNI_FALSE;
    }
}

extern "C" JNIEXPORT void JNICALL
Java_com_ainewsstudio_app_AndroidDiffusionBridge_nativeRelease(
    JNIEnv*, jobject, jlong handle) {
    delete reinterpret_cast<Diffusion*>(handle);
}
