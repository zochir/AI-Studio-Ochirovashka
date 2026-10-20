package com.ainewsstudio.app

import android.content.Context
import android.os.StatFs
import android.util.Base64
import android.webkit.JavascriptInterface
import android.webkit.WebView
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
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
        if (!nativeAvailable) return "NATIVE_UNAVAILABLE"
        try {
            ensureBundledTokenizer()
        } catch (e: Exception) {
            return "TOKENIZER_UNAVAILABLE:" + (e.message ?: "tokenizer.mtok missing")
        }
        val required = MODEL_FILES + "tokenizer.mtok"
        val missing = required.filter { !File(modelDir, it).isFile || File(modelDir, it).length() == 0L }
        return if (missing.isEmpty()) "MODEL_PRESENT" else "MODEL_MISSING:" + missing.joinToString(",")
    }

    @JavascriptInterface
    fun downloadModel(callbackId: String) {
        val id = callbackId.toIntOrNull() ?: return
        executor.execute {
            try {
                // Do not let unsupported ABIs download a multi-gigabyte model they cannot run.
                if (!nativeAvailable) {
                    throw IllegalStateException("Локальный движок недоступен для ABI этого устройства; загрузка модели отменена.")
                }
                ensureBundledTokenizer()
                val manifest = fetchManifest()
                val absent = MODEL_FILES.filterNot { manifest.containsKey(it) }
                if (absent.isNotEmpty()) throw IllegalStateException("Manifest без файлов: " + absent.joinToString(", "))
                val total = MODEL_FILES.sumOf { manifest.getValue(it).size }
                if (total < 1_000_000_000L) throw IllegalStateException("Размер модели меньше ожидаемого; скачивание остановлено.")
                // StatFs requires an existing path on Android. Create the private model directory
                // before querying free space so a first-time install does not fail with ENOENT.
                if (!modelDir.exists() && !modelDir.mkdirs()) {
                    throw IllegalStateException("Не удалось создать каталог модели в хранилище приложения.")
                }
                if (!modelDir.isDirectory) {
                    throw IllegalStateException("Путь для локальной модели не является каталогом.")
                }
                if (StatFs(modelDir.absolutePath).availableBytes < total + 150_000_000L) {
                    throw IllegalStateException("Недостаточно свободного места: требуется около " +
                        String.format(java.util.Locale.US, "%.2f GB", (total + 150_000_000L) / 1_000_000_000.0))
                }
                var completed = 0L
                notifyModel(id, 0, "Загрузка модели: " + humanBytes(total), false)
                for (name in MODEL_FILES) {
                    val meta = manifest.getValue(name)
                    val target = File(modelDir, name)
                    if (target.isFile && verifyFile(target, meta)) {
                        completed += meta.size
                        notifyModel(id, (completed * 100 / total).toInt(), "Проверен $name", false)
                        continue
                    }
                    target.delete()
                    val part = File(modelDir, "$name.part")
                    downloadOne(name, part, meta, id, completed, total)
                    if (!part.renameTo(target)) throw IllegalStateException("Не удалось сохранить $name")
                    completed += meta.size
                    notifyModel(id, (completed * 100 / total).toInt(), "Проверен $name", false)
                }
                notifyModel(id, 100, "Модель скачана и контрольные суммы проверены.", true)
            } catch (e: Throwable) {
                notifyModel(id, -1, e.message ?: e.javaClass.simpleName, true)
            }
        }
    }

    @JavascriptInterface
    fun generate(prompt: String, callbackId: String) {
        executor.execute {
            val result = try {
                if (!nativeAvailable) throw IllegalStateException("Нативная библиотека недоступна для ABI этого устройства.")
                ensureBundledTokenizer()
                val required = MODEL_FILES + "tokenizer.mtok"
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
                        val stableSeed = prompt.hashCode() and Int.MAX_VALUE
                        // 16 steps balances SD 1.5 detail and phone latency; the prompt-derived seed makes retries reproducible while panels differ.
                        val ok = nativeGenerate(nativeHandle, prompt, output.absolutePath, 16, stableSeed)
                        if (!ok || !isValidPng(output)) {
                            output.delete()
                            "window.nativeComicImageResult(" + callbackId.toIntOrNull() + ",null," +
                                org.json.JSONObject.quote("Локальная генерация не создала корректный PNG (проверены сигнатура и размеры).") + ");"
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

    fun close() {
        executor.execute {
            if (nativeHandle != 0L) {
                try { nativeRelease(nativeHandle) } catch (_: Throwable) {}
                nativeHandle = 0L
            }
        }
        executor.shutdown()
    }

    private fun isValidPng(file: File): Boolean {
        if (!file.isFile || file.length() < 33L) return false
        val header = ByteArray(24)
        try {
            file.inputStream().use { input ->
                var offset = 0
                while (offset < header.size) {
                    val count = input.read(header, offset, header.size - offset)
                    if (count <= 0) return false
                    offset += count
                }
            }
        } catch (_: Exception) {
            return false
        }
        val signature = byteArrayOf(0x89.toByte(), 0x50.toByte(), 0x4e.toByte(), 0x47.toByte(), 0x0d.toByte(), 0x0a.toByte(), 0x1a.toByte(), 0x0a.toByte())
        if (!header.copyOfRange(0, 8).contentEquals(signature)) return false
        if (String(header, 12, 4, Charsets.US_ASCII) != "IHDR") return false
        fun uint32(offset: Int): Long =
            ((header[offset].toLong() and 0xff) shl 24) or
            ((header[offset + 1].toLong() and 0xff) shl 16) or
            ((header[offset + 2].toLong() and 0xff) shl 8) or
            (header[offset + 3].toLong() and 0xff)
        return uint32(16) > 0L && uint32(20) > 0L
    }

    private data class ModelFile(val size: Long, val oid: String, val lfs: Boolean)

    private fun fetchManifest(): Map<String, ModelFile> {
        val url = URL("https://huggingface.co/api/models/$MODEL_REPO/tree/$MODEL_REVISION?recursive=true&expand=true")
        val connection = (url.openConnection() as HttpURLConnection).apply {
            connectTimeout = 20000; readTimeout = 60000
            setRequestProperty("User-Agent", "AI-Comic-Studio-Android")
        }
        try {
            if (connection.responseCode !in 200..299) throw IllegalStateException("Manifest HTTP ${connection.responseCode}")
            val array = JSONArray(connection.inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() })
            val result = mutableMapOf<String, ModelFile>()
            for (i in 0 until array.length()) {
                val item = array.getJSONObject(i)
                val name = item.optString("path")
                if (name !in MODEL_FILES) continue
                val lfs = item.optJSONObject("lfs")
                val oid = if (lfs != null) lfs.optString("oid").removePrefix("sha256:") else item.optString("oid")
                val size = if (lfs != null) lfs.optLong("size", -1L) else item.optLong("size", -1L)
                if (oid.isNotBlank() && size > 0) result[name] = ModelFile(size, oid, lfs != null)
            }
            return result
        } finally { connection.disconnect() }
    }

    private fun downloadOne(name: String, part: File, meta: ModelFile, id: Int, before: Long, total: Long) {
        // Keep a partial file after network interruption and resume with HTTP Range.
        // The final digest is still checked against the pinned Hub manifest.
        var offset = if (part.isFile) part.length() else 0L
        if (offset >= meta.size) {
            part.delete()
            offset = 0L
        }
        val connection = (URL("https://huggingface.co/$MODEL_REPO/resolve/$MODEL_REVISION/$name?download=true")
            .openConnection() as HttpURLConnection).apply {
            connectTimeout = 30000
            readTimeout = 90000
            setRequestProperty("User-Agent", "AI-Comic-Studio-Android")
            instanceFollowRedirects = true
            if (offset > 0L) setRequestProperty("Range", "bytes=$offset-")
        }
        try {
            val response = connection.responseCode
            if (response !in 200..299) {
                throw IllegalStateException("Не удалось скачать $name (HTTP $response)")
            }
            val append = if (offset > 0L && response == HttpURLConnection.HTTP_PARTIAL) {
                val range = connection.getHeaderField("Content-Range") ?: ""
                if (!range.startsWith("bytes $offset-")) {
                    throw IllegalStateException("Сервер вернул неверный диапазон для продолжения $name: $range")
                }
                true
            } else {
                // Some mirrors ignore Range and return the full file with HTTP 200.
                // In that case restart this one file rather than corrupting the model.
                if (response == HttpURLConnection.HTTP_PARTIAL) {
                    throw IllegalStateException("Неожиданный частичный ответ для $name")
                }
                offset = 0L
                false
            }

            val digest = MessageDigest.getInstance(if (meta.lfs) "SHA-256" else "SHA-1")
            if (!meta.lfs) digest.update("blob ${meta.size}\u0000".toByteArray(Charsets.UTF_8))
            if (append) {
                part.inputStream().buffered().use { input ->
                    val hashBuffer = ByteArray(256 * 1024)
                    while (true) {
                        val n = input.read(hashBuffer)
                        if (n < 0) break
                        digest.update(hashBuffer, 0, n)
                    }
                }
            }

            var received = offset
            var lastNotice = offset
            connection.inputStream.use { input ->
                part.outputStream().buffered().use { output ->
                    val buffer = ByteArray(256 * 1024)
                    while (true) {
                        val n = input.read(buffer)
                        if (n < 0) break
                        output.write(buffer, 0, n)
                        digest.update(buffer, 0, n)
                        received += n
                        if (received - lastNotice >= 4L * 1024 * 1024) {
                            lastNotice = received
                            notifyModel(id, ((before + received) * 100 / total).toInt().coerceIn(0, 99),
                                "Загрузка $name: ${humanBytes(received)} / ${humanBytes(meta.size)}", false)
                        }
                        if (received > meta.size) {
                            part.delete()
                            throw IllegalStateException("Размер $name превышает manifest")
                        }
                    }
                }
            }
            if (received != meta.size) {
                throw IllegalStateException("Неполная загрузка $name: $received из ${meta.size} байт. Можно повторить загрузку — продолжение поддерживается.")
            }
            val actual = digest.digest().joinToString("") { "%02x".format(it) }
            if (!actual.equals(meta.oid, true)) {
                part.delete()
                throw IllegalStateException("Контрольная сумма не совпала для $name; повреждённая частичная загрузка удалена.")
            }
        } catch (e: Throwable) {
            // Preserve valid-sized partial data after transient network errors so the next
            // attempt can resume. Oversized or complete-but-invalid files are discarded.
            if (part.isFile && part.length() >= meta.size) part.delete()
            throw e
        } finally {
            connection.disconnect()
        }
    }

    private fun verifyFile(file: File, meta: ModelFile): Boolean {
        if (!file.isFile || file.length() != meta.size) return false
        val digest = MessageDigest.getInstance(if (meta.lfs) "SHA-256" else "SHA-1")
        if (!meta.lfs) digest.update("blob ${meta.size}\u0000".toByteArray(Charsets.UTF_8))
        file.inputStream().buffered().use { input ->
            val buffer = ByteArray(256 * 1024)
            while (true) { val n = input.read(buffer); if (n < 0) break; digest.update(buffer, 0, n) }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }.equals(meta.oid, true)
    }

    private fun notifyModel(id: Int, percent: Int, message: String, done: Boolean) {
        val js = "window.nativeComicModelProgress($id,$percent,${JSONObject.quote(message)},$done);"
        webView.post { webView.evaluateJavascript(js, null) }
    }

    private fun humanBytes(bytes: Long): String = if (bytes >= 1_000_000_000L)
        String.format(java.util.Locale.US, "%.2f GB", bytes / 1_000_000_000.0)
    else String.format(java.util.Locale.US, "%.1f MB", bytes / 1_000_000.0)

    private fun ensureBundledTokenizer() {
        if (!modelDir.exists() && !modelDir.mkdirs()) {
            throw IllegalStateException("Не удалось создать каталог модели в хранилище приложения.")
        }
        if (!modelDir.isDirectory) {
            throw IllegalStateException("Путь для локальной модели не является каталогом.")
        }

        // The APK build writes this digest next to the tokenizer. Copy through a temporary
        // file and verify it before replacing the installed copy, so interrupted or corrupted
        // asset copies cannot be mistaken for a usable tokenizer.
        val expected = appContext.assets.open("tokenizer.sha256").bufferedReader(Charsets.UTF_8)
            .use { it.readText().trim().split(Regex("\\s+")).firstOrNull().orEmpty() }
        if (!expected.matches(Regex("[a-fA-F0-9]{64}"))) {
            throw IllegalStateException("Некорректная контрольная сумма встроенного токенизатора.")
        }

        val target = File(modelDir, "tokenizer.mtok")
        if (target.isFile && target.length() > 0L && sha256(target).equals(expected, ignoreCase = true)) return

        val part = File(modelDir, "tokenizer.mtok.part")
        part.delete()
        try {
            appContext.assets.open("tokenizer.mtok").use { input ->
                part.outputStream().buffered().use { output -> input.copyTo(output) }
            }
            if (!part.isFile || part.length() == 0L || !sha256(part).equals(expected, ignoreCase = true)) {
                throw IllegalStateException("Встроенный токенизатор не прошёл проверку SHA-256.")
            }
            if (target.exists() && !target.delete()) {
                throw IllegalStateException("Не удалось заменить повреждённый токенизатор.")
            }
            if (!part.renameTo(target)) {
                throw IllegalStateException("Не удалось установить токенизатор.")
            }
        } finally {
            part.delete()
        }
    }

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().buffered().use { input ->
            val buffer = ByteArray(64 * 1024)
            while (true) {
                val n = input.read(buffer)
                if (n < 0) break
                digest.update(buffer, 0, n)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    private external fun nativeCreate(modelPath: String): Long
    private external fun nativeGenerate(handle: Long, prompt: String, outputPath: String, steps: Int, seed: Int): Boolean
    private external fun nativeRelease(handle: Long)

    companion object {
        private const val MODEL_REPO = "taobao-mnn/stable-diffusion-v1-5-mnn-opencl"
        private const val MODEL_REVISION = "0dc4a5dbcee59a83bbc9694d13b10b4a7de4adc2"
        private val MODEL_FILES = listOf("alphas.txt", "text_encoder.mnn", "text_encoder.mnn.weight",
            "unet.mnn", "unet.mnn.weight", "vae_decoder.mnn", "vae_decoder.mnn.weight")
        private val nativeAvailable: Boolean = try {
            System.loadLibrary("MNN")
            System.loadLibrary("comicdiffusion")
            true
        } catch (_: UnsatisfiedLinkError) {
            false
        }
    }
}
