package com.ainewsstudio.app

import android.content.Context
import android.util.Base64
import android.webkit.JavascriptInterface
import android.webkit.WebView
import java.io.File
import java.util.concurrent.Executors

/**
 * Optional local MNN Diffusion bridge. It refuses to generate until a complete,
 * explicitly installed model bundle is present; it never downloads gigabytes silently.
 */
class AndroidDiffusionBridge(
    context: Context,
    private val webView: WebView
) {
    private val appContext = context.applicationContext
    private val executor = Executors.newSingleThreadExecutor()
    private val modelDir = File(appContext.filesDir, "models/sd15")
    private var nativeHandle: Long = 0

    @JavascriptInterface
    fun status(): String {
        val required = listOf("text_encoder.mnn", "unet.mnn", "vae_decoder.mnn", "tokenizer.mtok")
        val missing = required.filter { !File(modelDir, it).isFile || File(modelDir, it).length() == 0L }
        return if (missing.isEmpty()) "MODEL_PRESENT" else "MODEL_MISSING:" + missing.joinToString(",")
    }

    @JavascriptInterface
    fun generate(prompt: String, callbackId: String) {
        executor.execute {
            val result = try {
                val required = listOf("text_encoder.mnn", "unet.mnn", "vae_decoder.mnn", "tokenizer.mtok")
                val missing = required.filter { !File(modelDir, it).isFile || File(modelDir, it).length() == 0L }
                if (missing.isNotEmpty()) {
                    "window.nativeComicImageResult(" + callbackId.toIntOrNull() + ",null," +
                        org.json.JSONObject.quote("Локальная модель ещё не установлена. Не хватает: " + missing.joinToString(", ")) + ");"
                } else {
                    if (nativeHandle == 0L) nativeHandle = nativeCreate(modelDir.absolutePath)
                    if (nativeHandle == 0L) {
                        "window.nativeComicImageResult(" + callbackId.toIntOrNull() + ",null," +
                            org.json.JSONObject.quote("MNN не смог загрузить модель. Формат/токенизатор могут быть несовместимы.") + ");"
                    } else {
                        val output = File(appContext.cacheDir, "comic-${System.currentTimeMillis()}.png")
                        val ok = nativeGenerate(nativeHandle, prompt, output.absolutePath, 10, 42)
                        if (!ok || !output.isFile || output.length() < 128) {
                            "window.nativeComicImageResult(" + callbackId.toIntOrNull() + ",null," +
                                org.json.JSONObject.quote("Локальная генерация завершилась без корректного PNG.") + ");"
                        } else {
                            val encoded = Base64.encodeToString(output.readBytes(), Base64.NO_WRAP)
                            output.delete()
                            "window.nativeComicImageResult(" + callbackId.toIntOrNull() + ",\"data:image/png;base64,$encoded\",null);"
                        }
                    }
                }
            } catch (e: Throwable) {
                "window.nativeComicImageResult(" + callbackId.toIntOrNull() + ",null," +
                    org.json.JSONObject.quote("Ошибка локальной генерации: " + (e.message ?: e.javaClass.simpleName)) + ");"
            }
            webView.post { webView.evaluateJavascript(result, null) }
        }
    }

    private external fun nativeCreate(modelPath: String): Long
    private external fun nativeGenerate(handle: Long, prompt: String, outputPath: String, steps: Int, seed: Int): Boolean
    private external fun nativeRelease(handle: Long)

    companion object {
        init {
            System.loadLibrary("MNN")
            System.loadLibrary("comicdiffusion")
        }
    }
}
