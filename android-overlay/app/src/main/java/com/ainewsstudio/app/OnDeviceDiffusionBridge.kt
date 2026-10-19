package com.ainewsstudio.app

import android.app.Activity
import android.webkit.JavascriptInterface
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/**
 * Reports on-device diffusion readiness without pretending that the runtime is installed.
 *
 * The upstream MNN Android JNI API is not ABI-compatible with this app yet. Keep
 * inferenceAvailable false until the native library and an end-to-end inference
 * entry point are actually integrated and verified on a device.
 */
class OnDeviceDiffusionBridge(private val activity: Activity) {
    private val modelDirectory: File
        get() = File(activity.filesDir, "models/mnn-diffusion")

    @JavascriptInterface
    fun getStatusJson(): String {
        val nativeDir = File(activity.applicationInfo.nativeLibraryDir)
        val libraryNames = listOf("libmnnllmapp.so", "libmnn_diffusion.so")
        val presentLibraries = JSONArray()
        libraryNames.filter { File(nativeDir, it).isFile }.forEach { presentLibraries.put(it) }

        val modelFiles = JSONArray()
        val root = modelDirectory
        if (root.isDirectory) {
            root.walkTopDown()
                .filter { it.isFile }
                .take(200)
                .forEach { file ->
                    modelFiles.put(JSONObject()
                        .put("path", file.relativeTo(root).path)
                        .put("bytes", file.length()))
                }
        }

        val result = JSONObject()
            .put("runtimeLibraries", presentLibraries)
            .put("modelDirectory", root.absolutePath)
            .put("modelDirectoryExists", root.isDirectory)
            .put("modelFiles", modelFiles)
            .put("modelFileCount", modelFiles.length())
            .put("inferenceAvailable", false)
            .put(
                "message",
                "Локальная генерация MNN ещё не подключена: нативный inference-мост и проверенная модель отсутствуют."
            )
        return result.toString()
    }
}
