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
    Diffusion* diffusion = nullptr;
    try {
        const std::string path = fromJava(env, modelPath);
        if (path.empty()) return 0;
        diffusion = Diffusion::createDiffusion(
            path, STABLE_DIFFUSION_1_5, MNN_FORWARD_OPENCL, 0);
        if (!diffusion) return 0;
        if (!diffusion->load()) {
            delete diffusion;
            return 0;
        }
        return reinterpret_cast<jlong>(diffusion);
    } catch (const std::exception&) {
        delete diffusion;
        return 0;
    } catch (...) {
        delete diffusion;
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
    } catch (const std::exception&) {
        return JNI_FALSE;
    } catch (...) {
        return JNI_FALSE;
    }
}

extern "C" JNIEXPORT void JNICALL
Java_com_ainewsstudio_app_AndroidDiffusionBridge_nativeRelease(
    JNIEnv*, jobject, jlong handle) {
    delete reinterpret_cast<Diffusion*>(handle);
}
