package com.ainewsstudio.app

import android.app.Activity
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.speech.tts.Voice
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import org.json.JSONArray
import org.json.JSONObject
import java.util.Locale

class MainActivity : Activity(), TextToSpeech.OnInitListener {
    private lateinit var webView: WebView
    private lateinit var diffusionBridge: AndroidDiffusionBridge
    private var tts: TextToSpeech? = null
    private var ttsReady = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webChromeClient = WebChromeClient()
        webView.webViewClient = WebViewClient()
        webView.addJavascriptInterface(AndroidTtsBridge(), "AndroidTTS")
        diffusionBridge = AndroidDiffusionBridge(this, webView)
        webView.addJavascriptInterface(diffusionBridge, "AndroidDiffusion")
        setContentView(webView)
        tts = TextToSpeech(this, this)
        webView.loadUrl("file:///android_asset/index.html")
    }

    override fun onInit(status: Int) {
        ttsReady = status == TextToSpeech.SUCCESS
        if (ttsReady) {
            // Prefer Russian when available; users can choose any installed voice in the UI.
            val russian = tts?.voices?.firstOrNull { it.locale.language.equals("ru", true) }
            if (russian != null) tts?.voice = russian
        }
        if (::webView.isInitialized) {
            webView.post { webView.evaluateJavascript("window.nativeTtsReady && window.nativeTtsReady()", null) }
        }
    }

    inner class AndroidTtsBridge {
        @JavascriptInterface
        fun getVoicesJson(): String {
            if (!ttsReady) return "[]"
            val voices = tts?.voices ?: emptySet<Voice>()
            val arr = JSONArray()
            voices.filter { !it.isNetworkConnectionRequired }.sortedWith(compareBy<Voice>({ it.locale.language != "ru" }, { it.name })).forEach { v ->
                val item = JSONObject()
                item.put("name", v.name)
                item.put("lang", v.locale.toLanguageTag())
                item.put("default", v == tts?.voice)
                arr.put(item)
            }
            return arr.toString()
        }

        @JavascriptInterface
        fun speak(text: String, voiceName: String, rate: Float) {
            runOnUiThread {
                val engine = tts ?: return@runOnUiThread
                if (!ttsReady) return@runOnUiThread
                if (voiceName.isNotBlank()) {
                    engine.voices?.firstOrNull { it.name == voiceName }?.let { engine.voice = it }
                }
                engine.setSpeechRate(rate.coerceIn(0.5f, 2.0f))
                engine.speak(text, TextToSpeech.QUEUE_FLUSH, null, "ai-news-${System.currentTimeMillis()}")
            }
        }

        @JavascriptInterface
        fun stop() {
            runOnUiThread { tts?.stop() }
        }
    }

    override fun onDestroy() {
        webView.removeJavascriptInterface("AndroidTTS")
        webView.removeJavascriptInterface("AndroidDiffusion")
        if (::diffusionBridge.isInitialized) diffusionBridge.close()
        webView.destroy()
        tts?.stop()
        tts?.shutdown()
        super.onDestroy()
    }
}
