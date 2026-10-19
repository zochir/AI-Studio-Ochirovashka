from pathlib import Path
import re
import sys

project = Path(sys.argv[1])
activity = project / "app/src/main/java/com/ainewsstudio/app/MainActivity.kt"
source = activity.read_text(encoding="utf-8")

if "OnDeviceDiffusionBridge" not in source:
    anchor = 'webView.addJavascriptInterface(AndroidTtsBridge(), "AndroidTTS")'
    if anchor not in source:
        raise SystemExit("Cannot safely patch MainActivity: AndroidTTS bridge anchor not found")
    source = source.replace(
        anchor,
        anchor + '\n        webView.addJavascriptInterface(OnDeviceDiffusionBridge(this), "AndroidDiffusion")',
        1,
    )

    cleanup = 'webView.removeJavascriptInterface("AndroidTTS")'
    if cleanup not in source:
        raise SystemExit("Cannot safely patch MainActivity: AndroidTTS cleanup anchor not found")
    source = source.replace(
        cleanup,
        cleanup + '\n        webView.removeJavascriptInterface("AndroidDiffusion")',
        1,
    )
    activity.write_text(source, encoding="utf-8")

html_path = project / "app/src/main/assets/index.html"
html = html_path.read_text(encoding="utf-8")
marker = "<!-- AI_STUDIO_NATIVE_DIFFUSION_STATUS_V1 -->"
if marker not in html:
    module = r"""
<!-- AI_STUDIO_NATIVE_DIFFUSION_STATUS_V1 -->
<section id="nativeDiffusionStatus" style="margin:16px auto;padding:14px;max-width:1050px;border:1px solid #64748b;border-radius:12px;font:inherit">
  <h2 style="margin-top:0">Локальный движок Android</h2>
  <p id="nativeDiffusionMessage" role="status" aria-live="polite">Проверка нативного движка…</p>
  <button id="nativeDiffusionRefresh" type="button">Проверить готовность</button>
  <details><summary>Техническая диагностика</summary><pre id="nativeDiffusionDetails" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></details>
  <p style="font-size:.9em">Проверка показывает только наличие библиотек и файлов модели. Она не означает, что генерация изображений уже работает. До подключения и тестирования MNN inference кадры создаются через настроенный внешний API или ComfyUI.</p>
</section>
<script>
(function(){
  const message=document.getElementById("nativeDiffusionMessage");
  const details=document.getElementById("nativeDiffusionDetails");
  function refresh(){
    try{
      if(!window.AndroidDiffusion||typeof window.AndroidDiffusion.getStatusJson!=="function"){
        message.textContent="Нативная диагностика доступна только в Android APK. В браузере локальный Android-движок недоступен.";
        details.textContent="";
        return;
      }
      const status=JSON.parse(window.AndroidDiffusion.getStatusJson());
      message.textContent=status.message||"Статус локального движка получен.";
      details.textContent=JSON.stringify(status,null,2);
    }catch(error){
      message.textContent="Не удалось прочитать статус локального движка: "+error.message;
      details.textContent="";
    }
  }
  document.getElementById("nativeDiffusionRefresh").addEventListener("click",refresh);
  refresh();
})();
</script>
<!-- /AI_STUDIO_NATIVE_DIFFUSION_STATUS_V1 -->
"""
    if not re.search(r"</body\s*>", html, re.I):
        raise SystemExit("Could not find body end tag for native diffusion status panel")
    html = re.sub(r"</body\s*>", lambda m: module + "\n" + m.group(0), html, count=1, flags=re.I)
    html_path.write_text(html, encoding="utf-8")

print("Added explicit Android diffusion readiness diagnostics; no inference is claimed.")
