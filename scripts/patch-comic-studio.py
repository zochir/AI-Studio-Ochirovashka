from pathlib import Path
import re, sys

p = Path(sys.argv[1]) / "app/src/main/assets/index.html"
html = p.read_text(encoding="utf-8")
start_marker = "<!-- AI_STUDIO_COMIC_MODULE_V1 -->"
end_marker = "<!-- /AI_STUDIO_COMIC_MODULE_V1 -->"
module = r"""
<!-- AI_STUDIO_COMIC_MODULE_V1 -->
<style>
#comicLab{margin:20px auto;padding:18px;max-width:1050px;border:1px solid #94a3b8;border-radius:14px;background:#fff;color:#172033;font:inherit}
#comicLab *{box-sizing:border-box}#comicLab label{display:block;margin:10px 0 5px;font-weight:600}
#comicLab textarea,#comicLab input,#comicLab select{display:block;width:100%;padding:10px;border:1px solid #94a3b8;border-radius:8px;font:inherit}
#comicLab .comic-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
#comicLab button{padding:10px 14px;border:0;border-radius:9px;margin:12px 8px 0 0;background:#4f46e5;color:#fff;font:inherit;font-weight:650}
#comicLab button:disabled{opacity:.55}#comicLab .comic-note{font-size:.9em;line-height:1.45;opacity:.82}
#comicLab .comic-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:16px}
#comicLab .comic-panel{border:2px solid #172033;border-radius:8px;background:#fff;color:#172033;overflow:hidden;box-shadow:3px 4px 0 #172033}
#comicLab .comic-art{width:100%;aspect-ratio:1/1;display:grid;place-items:center;background:#dbeafe;font-size:40px;object-fit:cover}
#comicLab .comic-panel h3,#comicLab .comic-panel p{margin:10px;line-height:1.4}
</style>
<section id="comicLab" aria-labelledby="comicLabTitle">
<h2 id="comicLabTitle">Комикс-студия</h2>
<p class="comic-note" style="margin-top:-6px;font-weight:650">Разработчики: Очир Зулаев и Алиса</p>
<p class="comic-note">Сначала создайте раскадровку. Для настоящих изображений подключите совместимый с OpenAI Images API сервис. Ключ используется только в текущей сессии; для публичного приложения безопаснее обращаться к API через собственный сервер. Провайдер может блокировать прямые запросы из WebView через CORS.</p>
<label for="comicStory">Идея или сюжет</label><textarea id="comicStory" rows="4" placeholder="Опишите героев, место действия и события"></textarea>
<div class="comic-row"><div><label for="comicCount">Количество кадров</label><select id="comicCount"><option>3</option><option selected>4</option><option>6</option><option>8</option></select></div>
<div><label for="comicStyle">Визуальный стиль</label><select id="comicStyle"><option>Комикс с чёткими контурами</option><option>Манга</option><option>Акварельное фэнтези</option><option>Научная фантастика</option><option>Нуар</option></select></div></div>
<details><summary style="margin-top:14px;cursor:pointer;font-weight:650">Настройки ИИ-сценариста (необязательно)</summary>
<p class="comic-note">OpenAI-compatible Chat Completions. Ответ модели должен содержать JSON-массив с полями title, scene, dialogue.</p>
<label for="comicEndpoint">Chat-completions endpoint</label><input id="comicEndpoint" type="url" placeholder="https://example.com/v1/chat/completions">
<label for="comicModel">Модель текста</label><input id="comicModel" placeholder="text-model">
<label for="comicKey">Ключ текстового API</label><input id="comicKey" type="password" autocomplete="off">
</details>
<details><summary style="margin-top:14px;cursor:pointer;font-weight:650">Настройки генерации изображений</summary>
<p class="comic-note">Поддерживается формат OpenAI Images API: POST endpoint с полями model, prompt, size, n; ответ data[0].url или data[0].b64_json. Обычно для каждого кадра нужен отдельный запрос.</p>
<label for="comicImageEndpoint">Images endpoint</label><input id="comicImageEndpoint" type="url" placeholder="https://example.com/v1/images/generations">
<label for="comicImageModel">Модель изображений</label><input id="comicImageModel" placeholder="image-model">
<label for="comicImageKey">Ключ API изображений</label><input id="comicImageKey" type="password" autocomplete="off">
</details>
<details><summary style="margin-top:14px;cursor:pointer;font-weight:650">Локальная генерация через ComfyUI (основной режим)</summary>
<p class="comic-note">Запустите ComfyUI на своём компьютере и включите доступ из локальной сети. Вставьте API-workflow JSON из ComfyUI. В workflow укажите строку __PROMPT__ в поле positive prompt, которое нужно заменить описанием кадра. Для WebView/браузера ComfyUI должен разрешать CORS для origin приложения. Не открывайте ComfyUI в интернет без защиты.</p>
<label for="comicLocalEndpoint">Адрес локального ComfyUI</label><input id="comicLocalEndpoint" type="url" value="http://127.0.0.1:8188" placeholder="http://192.168.1.20:8188">
<label for="comicWorkflow">API workflow JSON</label><textarea id="comicWorkflow" rows="5" placeholder='{"1":{"class_type":"...","inputs":{"text":"__PROMPT__"}}}'></textarea>
<button id="comicGenerateLocal" type="button">Сгенерировать кадры локально</button>
</details>
<button id="comicGenerate" type="button">Создать раскадровку</button>
<button id="comicGenerateImages" type="button">Сгенерировать изображения кадров</button>
<button id="comicExport" type="button">Экспорт SVG-страницы</button>
<p id="comicStatus" role="status" aria-live="polite"></p><div id="comicPanels" class="comic-grid"></div>
</section>
<script>
(function(){
 const $=id=>document.getElementById(id);
 let panels=[];
 const names=["Завязка","Открытие","Развитие","Поворот","Кульминация","Развязка","Финал","Эпилог"];
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 function render(items){
  panels=items.map((p,i)=>({title:String(p.title||("Кадр "+(i+1)),),scene:String(p.scene||p.description||""),dialogue:String(p.dialogue||""),imageUrl:p.imageUrl||""}));
  $("comicPanels").innerHTML=panels.map((p,i)=>'<article class="comic-panel">'+(p.imageUrl?'<img class="comic-art" alt="Иллюстрация кадра '+(i+1)+'" src="'+esc(p.imageUrl)+'">':'<div class="comic-art" aria-hidden="true">🎨</div>')+'<h3>'+esc((i+1)+". "+p.title)+'</h3><p>'+esc(p.scene)+'</p>'+(p.dialogue?'<p><b>Реплика:</b> '+esc(p.dialogue)+'</p>':'')+'</article>').join("");
 }
 function localScenes(story,n){
  const sentences=story.replace(/\s+/g," ").split(/[.!?。！？]+/).map(x=>x.trim()).filter(Boolean),chunks=sentences.length?sentences:[story];
  return Array.from({length:n},(_,i)=>({title:names[i]||("Сцена "+(i+1)),scene:chunks[Math.min(chunks.length-1,Math.floor(i*chunks.length/n))]}));
 }
 async function generateScript(){
  const story=$("comicStory").value.trim(),n=Number($("comicCount").value),endpoint=$("comicEndpoint").value.trim(),model=$("comicModel").value.trim(),key=$("comicKey").value;
  if(!story){$("comicStatus").textContent="Введите идею или сюжет.";return;}
  $("comicGenerate").disabled=true;
  try{
   if(endpoint){
    if(!/^https?:\/\//i.test(endpoint)||!model||!key)throw Error("Для текстового ИИ укажите endpoint, модель и ключ.");
    const res=await fetch(endpoint,{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},body:JSON.stringify({model:model,temperature:.7,messages:[{role:"system",content:"Верни только JSON-массив из "+n+" объектов с полями title, scene, dialogue на русском языке. Это последовательные кадры одного комикса. Сохраняй внешний вид героев и причинно-следственную связь."},{role:"user",content:"Визуальный стиль: "+$("comicStyle").value+". Сюжет: "+story}]})});
    if(!res.ok)throw Error("Текстовый API вернул HTTP "+res.status);
    const data=await res.json(),raw=data.choices&&data.choices[0]&&data.choices[0].message&&data.choices[0].message.content;
    if(!raw)throw Error("В ответе текстового API нет сценария.");
    const parsed=JSON.parse(String(raw).replace(/^\x60\x60\x60(?:json)?\s*/i,"").replace(/\s*\x60\x60\x60$/,""));
    if(!Array.isArray(parsed)||!parsed.length)throw Error("Ожидался JSON-массив кадров.");
    render(parsed.slice(0,n));$("comicStatus").textContent="Сценарий создан ИИ. Следующий шаг — сгенерировать изображения кадров.";
   }else{
    render(localScenes(story,n));$("comicStatus").textContent="Создана локальная текстовая раскадровка. Для сценария от ИИ укажите настройки текстового API.";
   }
  }catch(e){$("comicStatus").textContent="Ошибка сценария: "+e.message;}
  finally{$("comicGenerate").disabled=false;}
 }
 async function generateImages(){
  const endpoint=$("comicImageEndpoint").value.trim(),model=$("comicImageModel").value.trim(),key=$("comicImageKey").value;
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  if(!endpoint||!model||!key){$("comicStatus").textContent="Для генерации изображений укажите endpoint, модель и ключ API изображений.";return;}
  if(!/^https?:\/\//i.test(endpoint)){$("comicStatus").textContent="Endpoint должен начинаться с http:// или https://.";return;}
  $("comicGenerateImages").disabled=true;
  try{
   let completed=0;
   for(let i=0;i<panels.length;i++){
    $("comicStatus").textContent="Генерация изображения "+(i+1)+" из "+panels.length+"…";
    const prompt="Create one finished comic panel illustration. Visual style: "+$("comicStyle").value+". Panel "+(i+1)+" of "+panels.length+". Story scene: "+panels[i].scene+". Character/dialogue context: "+panels[i].dialogue+". Keep recurring characters visually consistent, use a clear composition and no captions or lettering.";
    const res=await fetch(endpoint,{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},body:JSON.stringify({model:model,prompt:prompt,size:"1024x1024",n:1})});
    if(!res.ok)throw Error("Images API вернул HTTP "+res.status+" на кадре "+(i+1));
    const data=await res.json(),item=data.data&&data.data[0];
    if(!item)throw Error("Images API не вернул data[0] для кадра "+(i+1));
    const imageUrl=item.url||(item.b64_json?"data:image/png;base64,"+item.b64_json:"");
    if(!imageUrl)throw Error("Ответ кадра "+(i+1)+" не содержит url или b64_json.");
    panels[i].imageUrl=imageUrl;completed++;render(panels);
   }
   $("comicStatus").textContent="Готово: изображения получены для "+completed+" из "+panels.length+" кадров.";
  }catch(e){$("comicStatus").textContent="Генерация изображений остановлена: "+e.message+" Проверьте совместимость API, баланс и CORS; уже готовые кадры сохранены на экране.";}
  finally{$("comicGenerateImages").disabled=false;}
 }
 async function generateLocalImages(){
  const base=$("comicLocalEndpoint").value.trim().replace(/\/$/,""),workflowText=$("comicWorkflow").value.trim();
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  if(!base||!workflowText){$("comicStatus").textContent="Укажите адрес ComfyUI и API workflow JSON.";return;}
  let template;
  try{template=JSON.parse(workflowText);}catch(e){$("comicStatus").textContent="Workflow JSON некорректен: "+e.message;return;}
  $("comicGenerateLocal").disabled=true;
  try{
   for(let i=0;i<panels.length;i++){
    $("comicStatus").textContent="Локальная генерация: отправка кадра "+(i+1)+" из "+panels.length+"…";
    const prompt="Comic panel "+(i+1)+" of "+panels.length+". Style: "+$("comicStyle").value+". Scene: "+panels[i].scene+". Dialogue context: "+panels[i].dialogue+". Keep character design consistent. No text or lettering.";
    const replace=(v)=>typeof v==="string"?v.replace(/__PROMPT__/g,prompt):Array.isArray(v)?v.map(replace):v&&typeof v==="object"?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,replace(x)])):v;
    const res=await fetch(base+"/prompt",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt:replace(template)})});
    if(!res.ok)throw Error("ComfyUI /prompt HTTP "+res.status+"; проверьте адрес, доступ и CORS.");
    const queued=await res.json(),id=queued.prompt_id;
    if(!id)throw Error("ComfyUI не вернул prompt_id.");
    let history=null;
    for(let attempt=0;attempt<180;attempt++){
     await new Promise(resolve=>setTimeout(resolve,1000));
     const hr=await fetch(base+"/history/"+encodeURIComponent(id));
     if(!hr.ok)continue;
     const hd=await hr.json();history=hd[id]||hd[String(id)];
     if(history&&history.outputs)break;
     if(history&&history.status&&history.status.status_str==="error")throw Error("ComfyUI сообщил об ошибке генерации.");
    }
    if(!history||!history.outputs)throw Error("Истекло ожидание ComfyUI (3 минуты).");
    let image=null;
    for(const output of Object.values(history.outputs)){if(output&&Array.isArray(output.images)&&output.images.length){image=output.images[0];break;}}
    if(!image||!image.filename)throw Error("В результате workflow нет изображения. Проверьте SaveImage и выходы workflow.");
    const q=new URLSearchParams({filename:image.filename,subfolder:image.subfolder||"",type:image.type||"output"});
    panels[i].imageUrl=base+"/view?"+q.toString();render(panels);
   }
   $("comicStatus").textContent="ComfyUI завершил генерацию всех "+panels.length+" кадров. Изображения доступны по адресу локального движка.";
  }catch(e){$("comicStatus").textContent="Локальная генерация не завершена: "+e.message+" Проверьте, что ComfyUI запущен, workflow API-формата корректен и браузеру разрешён CORS.";}
  finally{$("comicGenerateLocal").disabled=false;}
 }
 function exportSvg(){
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  const escXml=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  const w=400,h=250,cols=2,rows=Math.ceil(panels.length/cols);
  const body=panels.map((p,i)=>{const x=(i%cols)*w+8,y=Math.floor(i/cols)*h+8;const image=p.imageUrl?'<text x="10" y="90" font-size="12">Иллюстрация создана; откройте приложение для просмотра</text>':'<text x="190" y="70" font-size="32" text-anchor="middle">🎨</text>';return '<g transform="translate('+x+' '+y+')"><rect width="384" height="234" rx="8" fill="#fff" stroke="#172033" stroke-width="3"/><rect x="8" y="8" width="368" height="100" fill="#dbeafe"/>'+image+'<text x="14" y="134" font-size="17" font-weight="bold">'+escXml((i+1)+". "+p.title.slice(0,32))+'</text><foreignObject x="14" y="144" width="350" height="78"><div xmlns="http://www.w3.org/1999/xhtml" style="font:14px sans-serif">'+escXml(p.scene.slice(0,150))+'</div></foreignObject></g>';}).join("");
  const svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+(cols*w)+'" height="'+(rows*h)+'" viewBox="0 0 '+(cols*w)+' '+(rows*h)+'">'+body+'</svg>';
  const url=URL.createObjectURL(new Blob([svg],{type:"image/svg+xml;charset=utf-8"})),a=document.createElement("a");a.href=url;a.download="comic-storyboard.svg";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  $("comicStatus").textContent="SVG-страница подготовлена. Внешние изображения не встраиваются в SVG-файл; для экспорта с картинками потребуется отдельная упаковка изображений.";
 }
 $("comicGenerate").addEventListener("click",generateScript);
 $("comicGenerateImages").addEventListener("click",generateImages);
 $("comicGenerateLocal").addEventListener("click",generateLocalImages);
 $("comicExport").addEventListener("click",exportSvg);
})();
</script>
<!-- /AI_STUDIO_COMIC_MODULE_V1 -->
"""
if start_marker in html:
    before, rest = html.split(start_marker, 1)
    _, after = rest.split(end_marker, 1)
    html = before + module + after
else:
    if not re.search(r"</body\s*>", html, re.I):
        raise SystemExit("Could not find body end tag")
    html = re.sub(r"</body\s*>", lambda m: module + "\n" + m.group(0), html, count=1, flags=re.I)
p.write_text(html, encoding="utf-8")
print("Comic Studio updated: storyboard, optional text API, image API integration, SVG export.")
