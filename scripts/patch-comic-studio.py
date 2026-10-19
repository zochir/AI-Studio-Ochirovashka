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
#comicLab .comic-art{width:100%;aspect-ratio:1/1;display:grid;place-items:center;background:#e2e8f0;color:#334155;font-size:15px;text-align:center;padding:18px;object-fit:cover}#comicLab .comic-art-placeholder{font-weight:650;line-height:1.5}
#comicLab .comic-panel h3,#comicLab .comic-panel p{margin:10px;line-height:1.4}
</style>
<section id="comicLab" aria-labelledby="comicLabTitle">
<h2 id="comicLabTitle">Комикс-студия</h2>
<p class="comic-note" style="margin-top:-6px;font-weight:650">Разработчики: Очир Зулаев и Алиса</p>
<p class="comic-note">Важно: «Создать раскадровку» формирует только текст кадров — это ещё не генерация рисунков. Серый блок означает, что изображение не создано. Чтобы получить реальные иллюстрации бесплатно локально, настройте ComfyUI и вставьте его API workflow; альтернативно укажите совместимый Images API. Ключ используется только в текущей сессии; для публичного приложения безопаснее обращаться к API через собственный сервер. Провайдер может блокировать прямые запросы из WebView через CORS.</p>
<label for="comicStory">Идея или сюжет</label><textarea id="comicStory" rows="4" placeholder="Опишите героев, место действия и события"></textarea>
<label for="comicCharacterName">Имя нового персонажа</label><input id="comicCharacterName" maxlength="80" placeholder="Например, Лея"><label for="comicCharacterLook">Уникальная внешность и отличительные детали</label><textarea id="comicCharacterLook" rows="2" placeholder="Возраст, лицо, волосы, одежда, телосложение, аксессуары, характерные детали"></textarea><button id="comicAddCharacter" type="button">Добавить персонажа</button><label for="comicCharacters">Карточки персонажей — сохраняйте постоянную внешность между кадрами</label><textarea id="comicCharacters" rows="4" placeholder="Добавьте одного или нескольких персонажей выше. Можно также редактировать карточки вручную."></textarea>
<div class="comic-row"><div><label for="comicMood">Атмосфера</label><select id="comicMood"><option>Приключение и динамика</option><option>Тёплая и уютная</option><option>Мрачная и напряжённая</option><option>Эпическая и масштабная</option><option>Юмор и лёгкость</option><option>Меланхоличная</option></select></div><div><label for="comicComposition">Композиция кадра</label><select id="comicComposition"><option>Автоматически по сцене</option><option>Кинематографический широкий план</option><option>Портрет и эмоции</option><option>Динамичный ракурс и движение</option><option>Общий план окружения</option></select></div></div>
<div class="comic-row"><div><label for="comicCount">Количество кадров</label><select id="comicCount"><option>3</option><option selected>4</option><option>6</option><option>8</option></select></div>
<div><label for="comicStyle">Визуальный стиль</label><select id="comicStyle"><option>Комикс с чёткими контурами</option><option>Графический роман</option><option>Манга</option><option>Аниме</option><option>Акварельное фэнтези</option><option>Карандашный скетч</option><option>Ретро-комикс</option><option>Пиксель-арт</option><option>3D-анимация</option><option>Научная фантастика</option><option>Нуар</option><option>Поп-арт</option><option>Европейский альбомный комикс</option></select></div></div>
<details><summary style="margin-top:14px;cursor:pointer;font-weight:650">Настройки ИИ-сценариста (необязательно)</summary>
<p class="comic-note">OpenAI-compatible Chat Completions (например, локальный Ollama /v1/chat/completions). Ответ модели должен содержать JSON-массив с полями title, scene, dialogue. Для локального сервера ключ обычно не нужен.</p>
<label for="comicEndpoint">Chat-completions endpoint</label><input id="comicEndpoint" type="url" placeholder="https://example.com/v1/chat/completions">
<label for="comicModel">Модель текста</label><input id="comicModel" placeholder="text-model">
<label for="comicKey">Ключ текстового API</label><input id="comicKey" type="password" autocomplete="off">
</details>
<details><summary style="margin-top:14px;cursor:pointer;font-weight:650">Настройки генерации изображений</summary>
<p class="comic-note">Есть два режима: OpenAI-compatible Images API и Pollinations. Pollinations требует API-ключ с сайта провайдера; доступность и стоимость зависят от вашей квоты и выбранной модели. Не публикуйте секретный ключ.</p><button id="comicUsePollinations" type="button">Настроить Pollinations</button><p class="comic-note">Обычный Images API: POST с model, prompt, size, n; ответ data[0].url или data[0].b64_json. Кнопка Pollinations переключает генератор на прямой image endpoint.</p>
<label for="comicImageEndpoint">Images endpoint</label><input id="comicImageEndpoint" type="url" placeholder="https://example.com/v1/images/generations">
<label for="comicImageModel">Модель изображений</label><input id="comicImageModel" placeholder="image-model">
<label for="comicImageKey">Ключ API изображений</label><input id="comicImageKey" type="password" autocomplete="off">
</details>
<details><summary style="margin-top:14px;cursor:pointer;font-weight:650">Локальная генерация через ComfyUI (основной режим)</summary>
<p class="comic-note">Запустите ComfyUI на своём компьютере и включите доступ из локальной сети. Вставьте API-workflow JSON из ComfyUI. В workflow укажите строку __PROMPT__ в поле positive prompt, которое нужно заменить описанием кадра. Для WebView/браузера ComfyUI должен разрешать CORS для origin приложения. Не открывайте ComfyUI в интернет без защиты.</p>
<label for="comicLocalEndpoint">Адрес локального ComfyUI</label><input id="comicLocalEndpoint" type="url" placeholder="http://192.168.1.20:8188">
<label for="comicWorkflow">API workflow JSON</label><textarea id="comicWorkflow" rows="5" placeholder='{"1":{"class_type":"...","inputs":{"text":"__PROMPT__"}}}'></textarea>
<button id="comicCheckLocal" type="button">Проверить подключение</button><button id="comicGenerateLocal" type="button">Сгенерировать кадры локально</button>
</details>
<button id="comicGenerate" type="button">Создать раскадровку</button>
<button id="comicGenerateImages" type="button">Сгенерировать изображения кадров</button>
<button id="comicSave" type="button">Сохранить проект</button><button id="comicLoad" type="button">Загрузить проект</button><button id="comicExportProject" type="button">Экспорт проекта JSON</button><button id="comicImportProject" type="button">Импорт проекта JSON</button><input id="comicProjectFile" type="file" accept="application/json,.json" hidden><button id="comicExport" type="button">Экспорт SVG-страницы</button>
<p id="comicStatus" role="status" aria-live="polite"></p><div id="comicPanels" class="comic-grid"></div>
</section>
<script>
(function(){
 const $=id=>document.getElementById(id);
 let panels=[];
 const PROJECT_KEY="ai-studio-comic-project-v1";
 const names=["Завязка","Открытие","Развитие","Поворот","Кульминация","Развязка","Финал","Эпилог"];
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 async function fetchTimed(url,options,timeoutMs=45000){
  const controller=typeof AbortController!=="undefined"?new AbortController():null;
  const opts=Object.assign({},options||{});
  if(controller)opts.signal=controller.signal;
  let timer;
  try{
   const timeout=new Promise((_,reject)=>{timer=setTimeout(()=>{if(controller)controller.abort();reject(Error("Превышено время ожидания ответа ("+Math.round(timeoutMs/1000)+" с)."));},timeoutMs);});
   return await Promise.race([fetch(url,opts),timeout]);
  }finally{clearTimeout(timer);}
 }

 function render(items){
  panels=items.map((p,i)=>({title:String(p.title||("Кадр "+(i+1)),),scene:String(p.scene||p.description||""),dialogue:String(p.dialogue||""),imageUrl:p.imageUrl||""}));
  $("comicPanels").innerHTML=panels.map((p,i)=>'<article class="comic-panel">'+(p.imageUrl?'<img class="comic-art" alt="Иллюстрация кадра '+(i+1)+'" src="'+esc(p.imageUrl)+'">':'<div class="comic-art comic-art-placeholder">Иллюстрация ещё не создана<br>Настройте генератор и нажмите «Сгенерировать изображения кадров»</div>')+'<h3>'+esc((i+1)+". "+p.title)+'</h3><p>'+esc(p.scene)+'</p>'+(p.dialogue?'<p><b>Реплика:</b> '+esc(p.dialogue)+'</p>':'')+'</article>').join("");
 }
 function saveProject(){
  try{
   const data={version:1,story:$("comicStory").value,characters:$("comicCharacters").value,mood:$("comicMood").value,composition:$("comicComposition").value,count:$("comicCount").value,style:$("comicStyle").value,endpoint:$("comicEndpoint").value,model:$("comicModel").value,imageEndpoint:$("comicImageEndpoint").value,imageModel:$("comicImageModel").value,localEndpoint:$("comicLocalEndpoint").value,workflow:$("comicWorkflow").value,panels:panels};
   localStorage.setItem(PROJECT_KEY,JSON.stringify(data));
   $("comicStatus").textContent="Проект сохранён на этом устройстве ("+panels.length+" кадров).";
  }catch(e){$("comicStatus").textContent="Не удалось сохранить проект: "+e.message+". Возможно, изображения занимают слишком много места; экспортируйте их отдельно.";}
 }
 function loadProject(){
  try{
   const raw=localStorage.getItem(PROJECT_KEY);
   if(!raw){$("comicStatus").textContent="Сохранённый проект на этом устройстве не найден.";return;}
   const data=JSON.parse(raw);
   if(!data||data.version!==1||!Array.isArray(data.panels))throw Error("неподдерживаемый формат проекта");
   $("comicStory").value=String(data.story||"");
   $("comicCharacters").value=String(data.characters||"");
   $("comicMood").value=String(data.mood||"Приключение и динамика");
   $("comicComposition").value=String(data.composition||"Автоматически по сцене");
   $("comicCount").value=String(data.count||4);
   $("comicStyle").value=String(data.style||"Комикс с чёткими контурами");
   $("comicEndpoint").value=String(data.endpoint||"");
   $("comicModel").value=String(data.model||"");
   $("comicImageEndpoint").value=String(data.imageEndpoint||"");
   $("comicImageModel").value=String(data.imageModel||"");
   $("comicLocalEndpoint").value=String(data.localEndpoint||"");
   $("comicWorkflow").value=String(data.workflow||"");
   render(data.panels);
   $("comicStatus").textContent="Проект загружен ("+panels.length+" кадров).";
  }catch(e){$("comicStatus").textContent="Не удалось загрузить проект: "+e.message;}
 }
 function localScenes(story,n){
  const sentences=story.replace(/\s+/g," ").split(/[.!?。！？]+/).map(x=>x.trim()).filter(Boolean),chunks=sentences.length?sentences:[story];
  return Array.from({length:n},(_,i)=>({title:names[i]||("Сцена "+(i+1)),scene:chunks[Math.min(chunks.length-1,Math.floor(i*chunks.length/n))]}));
 }
 function projectData(){
  return {format:"ai-comic-studio-project",version:1,story:$("comicStory").value,characters:$("comicCharacters").value,mood:$("comicMood").value,composition:$("comicComposition").value,count:$("comicCount").value,style:$("comicStyle").value,endpoint:$("comicEndpoint").value,model:$("comicModel").value,imageEndpoint:$("comicImageEndpoint").value,imageModel:$("comicImageModel").value,localEndpoint:$("comicLocalEndpoint").value,workflow:$("comicWorkflow").value,panels:panels};
 }
 function downloadText(filename,text,mime){
  const url=URL.createObjectURL(new Blob([text],{type:mime})),a=document.createElement("a");
  a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 async function exportProject(){
  $("comicExportProject").disabled=true;$("comicStatus").textContent="Подготовка переносимого проекта…";
  try{
   const data=projectData();
   for(let i=0;i<data.panels.length;i++){
    const src=data.panels[i].imageUrl;if(!src||/^data:image\//i.test(src))continue;
    try{
     const response=await fetchTimed(src,{},15000);if(!response.ok)throw Error("HTTP "+response.status);
     const blob=await response.blob(),bytes=new Uint8Array(await blob.arrayBuffer());let binary="";
     for(let j=0;j<bytes.length;j+=0x8000)binary+=String.fromCharCode(...bytes.subarray(j,j+0x8000));
     data.panels[i].imageUrl="data:"+(blob.type||"image/png")+";base64,"+btoa(binary);
    }catch(e){data.panels[i].imageExportWarning="Изображение осталось внешней ссылкой: браузер не разрешил встроить файл (возможен CORS).";}
   }
   downloadText("comic-project.json",JSON.stringify(data,null,2),"application/json;charset=utf-8");
   const embedded=data.panels.filter(x=>/^data:image\//i.test(x.imageUrl||"")).length,external=data.panels.filter(x=>x.imageUrl&&!/^data:image\//i.test(x.imageUrl)).length;
   $("comicStatus").textContent="Проект JSON экспортирован. Встроенных изображений: "+embedded+"; внешних ссылок: "+external+". Ключи API не экспортируются.";
  }catch(e){$("comicStatus").textContent="Не удалось экспортировать проект: "+e.message;}
  finally{$("comicExportProject").disabled=false;}
 }
 function importProjectFile(file){
  if(!file)return;const reader=new FileReader();
  reader.onload=()=>{
   try{
    const data=JSON.parse(String(reader.result||""));
    if(!data||data.format!=="ai-comic-studio-project"||data.version!==1||!Array.isArray(data.panels))throw Error("неподдерживаемый формат файла проекта");
    $("comicStory").value=String(data.story||"");$("comicCharacters").value=String(data.characters||"");
    $("comicMood").value=String(data.mood||"Приключение и динамика");$("comicComposition").value=String(data.composition||"Автоматически по сцене");
    $("comicCount").value=String(data.count||4);$("comicStyle").value=String(data.style||"Комикс с чёткими контурами");
    $("comicEndpoint").value=String(data.endpoint||"");$("comicModel").value=String(data.model||"");
    $("comicImageEndpoint").value=String(data.imageEndpoint||"");$("comicImageModel").value=String(data.imageModel||"");
    $("comicLocalEndpoint").value=String(data.localEndpoint||"");$("comicWorkflow").value=String(data.workflow||"");
    render(data.panels);saveProject();$("comicStatus").textContent="Проект импортирован: "+panels.length+" кадров. Секретные ключи API нужно ввести заново.";
   }catch(e){$("comicStatus").textContent="Не удалось импортировать проект: "+e.message;}
  };
  reader.onerror=()=>{$("comicStatus").textContent="Не удалось прочитать файл проекта."};reader.readAsText(file);
 }
 async function generateScript(){
  const story=$("comicStory").value.trim(),characters=$("comicCharacters").value.trim(),mood=$("comicMood").value,composition=$("comicComposition").value,n=Number($("comicCount").value),endpoint=$("comicEndpoint").value.trim(),model=$("comicModel").value.trim(),key=$("comicKey").value;
  if(!story){$("comicStatus").textContent="Введите идею или сюжет.";return;}
  $("comicGenerate").disabled=true;
  try{
   if(endpoint){
    if(!/^https?:\/\//i.test(endpoint)||!model)throw Error("Для текстового ИИ укажите корректный endpoint и модель. Ключ нужен только если его требует сервер.");
    const res=await fetchTimed(endpoint,{method:"POST",headers:Object.assign({"Content-Type":"application/json"},key?{"Authorization":"Bearer "+key}:{}),body:JSON.stringify({model:model,temperature:.7,messages:[{role:"system",content:"Верни только JSON-массив из "+n+" объектов с полями title, scene, dialogue на русском языке. Это последовательные кадры одного комикса. Сохраняй внешний вид героев, причинно-следственную связь, разнообразие планов и эмоций. Учитывай паспорт персонажей и атмосферу."},{role:"user",content:"Визуальный стиль: "+$("comicStyle").value+". Атмосфера: "+mood+". Композиция: "+composition+". Паспорт персонажей: "+(characters||"создай подходящих сюжету героев и сохраняй их внешний вид")+". Сюжет: "+story}]})});
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
  if(!endpoint||!model){$("comicStatus").textContent="Для генерации изображений укажите endpoint и модель. Ключ нужен только если его требует сервер.";return;}
  if(!/^https?:\/\//i.test(endpoint)){$("comicStatus").textContent="Endpoint должен начинаться с http:// или https://.";return;}
  $("comicGenerateImages").disabled=true;
  try{
   let completed=0;
   for(let i=0;i<panels.length;i++){
    $("comicStatus").textContent="Генерация изображения "+(i+1)+" из "+panels.length+"…";
    const prompt="Create one finished comic panel illustration, not an icon, logo, paint palette, easel, artist tools, or placeholder. Depict the actual scene described below. No text, letters, watermark, logo, paint palette, or easel in the image. Visual style: "+$("comicStyle").value+". Mood: "+$("comicMood").value+". Composition: "+$("comicComposition").value+". Panel "+(i+1)+" of "+panels.length+". Character design bible (preserve exact appearance, outfit, age and distinguishing marks in every panel): "+($("comicCharacters").value.trim()||"derive a coherent recurring design from the story and keep it unchanged")+". Story scene: "+panels[i].scene+". Character/dialogue context: "+panels[i].dialogue+". Vary shot size and camera angle to fit the scene while preserving character identity. No captions or lettering.";
    let imageUrl="";
     if(endpoint.replace(/\/$/,"")==="https://gen.pollinations.ai/image"){
      const url=endpoint.replace(/\/$/,"")+"/"+encodeURIComponent(prompt)+"?model="+encodeURIComponent(model);
      const res=await fetchTimed(url,{method:"GET",headers:key?{"Authorization":"Bearer "+key}:{}});
      if(!res.ok)throw Error("Pollinations вернул HTTP "+res.status+" на кадре "+(i+1));
      const blob=await res.blob(),bytes=new Uint8Array(await blob.arrayBuffer());let binary="";
      for(let j=0;j<bytes.length;j+=0x8000)binary+=String.fromCharCode(...bytes.subarray(j,j+0x8000));
      imageUrl="data:"+(blob.type||"image/jpeg")+";base64,"+btoa(binary);
     }else{
      const res=await fetchTimed(endpoint,{method:"POST",headers:Object.assign({"Content-Type":"application/json"},key?{"Authorization":"Bearer "+key}:{}),body:JSON.stringify({model:model,prompt:prompt,size:"1024x1024",n:1})});
      if(!res.ok)throw Error("Images API вернул HTTP "+res.status+" на кадре "+(i+1));
      const data=await res.json(),item=data.data&&data.data[0];
      if(!item)throw Error("Images API не вернул data[0] для кадра "+(i+1));
      imageUrl=item.url||(item.b64_json?"data:image/png;base64,"+item.b64_json:"");
     }
     if(!imageUrl)throw Error("Ответ кадра "+(i+1)+" не содержит изображения.");
     panels[i].imageUrl=imageUrl;completed++;render(panels);
   }
   $("comicStatus").textContent="Готово: изображения получены для "+completed+" из "+panels.length+" кадров.";
  }catch(e){$("comicStatus").textContent="Генерация изображений остановлена: "+e.message+" Проверьте совместимость API, баланс и CORS; уже готовые кадры сохранены на экране.";}
  finally{$("comicGenerateImages").disabled=false;}
 }
 async function checkLocalConnection(){
  const base=$("comicLocalEndpoint").value.trim().replace(/\/$/,"");
  if(!base){$("comicStatus").textContent="Укажите адрес ComfyUI.";return;}
  const button=$("comicCheckLocal");button.disabled=true;
  $("comicStatus").textContent="Проверка соединения с ComfyUI…";
  try{
   const controller=typeof AbortController!=="undefined"?new AbortController():null;
   const timer=setTimeout(()=>{if(controller)controller.abort();},8000);
   let response;
   try{response=await fetch(base+"/system_stats",{method:"GET",signal:controller?controller.signal:undefined});}
   finally{clearTimeout(timer);}
   if(!response.ok)throw Error("HTTP "+response.status);
   const info=await response.json();
   const devices=Array.isArray(info.devices)?info.devices.length:0;
   $("comicStatus").textContent="ComfyUI доступен. Ответ /system_stats получен"+(devices?"; устройств: "+devices:"")+". Теперь можно запускать генерацию.";
  }catch(e){
   const reason=e&&e.name==="AbortError"?"тайм-аут (8 секунд)":e.message;
   $("comicStatus").textContent="Не удалось подключиться к ComfyUI: "+reason+". Проверьте адрес, что сервер запущен, доступ по локальной сети и CORS.";
  }finally{button.disabled=false;}
 }
 async function generateLocalImages(){
  const base=$("comicLocalEndpoint").value.trim().replace(/\/$/,""),workflowText=$("comicWorkflow").value.trim();
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  if(!base||!workflowText){$("comicStatus").textContent="Укажите адрес ComfyUI и API workflow JSON.";return;}
  let template;
  try{template=JSON.parse(workflowText);}catch(e){$("comicStatus").textContent="Workflow JSON некорректен: "+e.message;return;}
   let placeholderCount=0;const countPlaceholders=v=>{if(typeof v==="string"){const m=v.match(/__PROMPT__/g);placeholderCount+=m?m.length:0;}else if(Array.isArray(v))v.forEach(countPlaceholders);else if(v&&typeof v==="object")Object.values(v).forEach(countPlaceholders);};countPlaceholders(template);
   if(!placeholderCount){$("comicStatus").textContent="Workflow не содержит __PROMPT__. Добавьте этот маркер в positive prompt API-workflow, иначе каждый кадр будет генерироваться по одному и тому же запросу.";return;}
  $("comicGenerateLocal").disabled=true;
  try{
   for(let i=0;i<panels.length;i++){
    $("comicStatus").textContent="Локальная генерация: отправка кадра "+(i+1)+" из "+panels.length+"…";
    const prompt="Create an actual narrative comic illustration, not an icon, logo, paint palette, easel, or placeholder. Depict the described scene. No text, letters, watermark, logo, paint palette, or easel. Comic panel "+(i+1)+" of "+panels.length+". Style: "+$("comicStyle").value+". Mood: "+$("comicMood").value+". Composition: "+$("comicComposition").value+". Character design bible (preserve exact appearance, outfit, age and distinguishing marks): "+($("comicCharacters").value.trim()||"derive a coherent recurring design from the story and keep it unchanged")+". Scene: "+panels[i].scene+". Dialogue context: "+panels[i].dialogue+". Vary shot size and camera angle according to scene while preserving character identity. No text or lettering.";
    const replace=(v)=>typeof v==="string"?v.replace(/__PROMPT__/g,prompt):Array.isArray(v)?v.map(replace):v&&typeof v==="object"?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,replace(x)])):v;
    const res=await fetchTimed(base+"/prompt",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt:replace(template)})});
    if(!res.ok)throw Error("ComfyUI /prompt HTTP "+res.status+"; проверьте адрес, доступ и CORS.");
    const queued=await res.json(),id=queued.prompt_id;
    if(!id)throw Error("ComfyUI не вернул prompt_id.");
    let history=null;
    for(let attempt=0;attempt<180;attempt++){
     await new Promise(resolve=>setTimeout(resolve,1000));
     const hr=await fetchTimed(base+"/history/"+encodeURIComponent(id),{},10000);
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
 async function exportSvg(){
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  const escXml=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  const imageData=async src=>{
   if(!src)return "";
   if(/^data:image\//i.test(src))return src;
   try{
    const response=await fetchTimed(src,{},15000);
    if(!response.ok)throw Error("HTTP "+response.status);
    const blob=await response.blob();
    const bytes=new Uint8Array(await blob.arrayBuffer());
    let binary="";
    for(let i=0;i<bytes.length;i+=0x8000)binary+=String.fromCharCode(...bytes.subarray(i,i+0x8000));
    const mime=blob.type||"image/png";
    return "data:"+mime+";base64,"+btoa(binary);
   }catch(e){return "";}
  };
  $("comicExport").disabled=true;
  $("comicStatus").textContent="Подготовка экспорта: встраиваем доступные изображения…";
  try{
   const w=400,h=250,cols=2,rows=Math.ceil(panels.length/cols),images=await Promise.all(panels.map(p=>imageData(p.imageUrl)));
   const body=panels.map((p,i)=>{const x=(i%cols)*w+8,y=Math.floor(i/cols)*h+8;const art=images[i]?'<image x="8" y="8" width="368" height="100" preserveAspectRatio="xMidYMid slice" href="'+images[i]+'"/>':'<rect x="8" y="8" width="368" height="100" fill="#e2e8f0"/><text x="192" y="48" font-size="15" text-anchor="middle" fill="#334155">Иллюстрация не создана</text>';return '<g transform="translate('+x+' '+y+')"><rect width="384" height="234" rx="8" fill="#fff" stroke="#172033" stroke-width="3"/>'+art+'<text x="14" y="134" font-size="17" font-weight="bold">'+escXml((i+1)+". "+p.title.slice(0,32))+'</text><foreignObject x="14" y="144" width="350" height="78"><div xmlns="http://www.w3.org/1999/xhtml" style="font:14px sans-serif">'+escXml(p.scene.slice(0,150))+(p.dialogue?'<br/><b>Реплика:</b> '+escXml(p.dialogue.slice(0,100)):"")+'</div></foreignObject></g>';}).join("");
   const svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+(cols*w)+'" height="'+(rows*h)+'" viewBox="0 0 '+(cols*w)+' '+(rows*h)+'">'+body+'</svg>';
   const url=URL.createObjectURL(new Blob([svg],{type:"image/svg+xml;charset=utf-8"})),a=document.createElement("a");a.href=url;a.download="comic-storyboard.svg";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
   const embedded=images.filter(Boolean).length;
   $("comicStatus").textContent="Экспорт SVG подготовлен. Встроено изображений: "+embedded+" из "+panels.length+". Если локальный сервер блокирует CORS, соответствующий кадр экспортирован как заглушка.";
  }catch(e){$("comicStatus").textContent="Не удалось экспортировать комикс: "+e.message;}
  finally{$("comicExport").disabled=false;}
 }
 $("comicAddCharacter").addEventListener("click",()=>{const name=$("comicCharacterName").value.trim(),look=$("comicCharacterLook").value.trim();if(!name||!look){$("comicStatus").textContent="Для карточки персонажа укажите имя и описание внешности.";return;}const card=name+" — "+look;const current=$("comicCharacters").value.trim();if(current.split("\n").some(line=>line.trim().toLocaleLowerCase()===card.toLocaleLowerCase())){$("comicStatus").textContent="Такая карточка уже добавлена.";return;}$("comicCharacters").value=current?current+"\n"+card:card;$("comicCharacterName").value="";$("comicCharacterLook").value="";$("comicStatus").textContent="Карточка персонажа «"+name+"» добавлена. Описание будет учитываться при генерации кадров.";});
 $("comicGenerate").addEventListener("click",generateScript);
 $("comicGenerateImages").addEventListener("click",generateImages);
 $("comicUsePollinations").addEventListener("click",()=>{$("comicImageEndpoint").value="https://gen.pollinations.ai/image/";$("comicImageModel").value="flux";$("comicStatus").textContent="Pollinations настроен. Введите API-ключ провайдера и учитывайте лимиты/стоимость выбранной модели.";});
 $("comicCheckLocal").addEventListener("click",checkLocalConnection);
 $("comicGenerateLocal").addEventListener("click",generateLocalImages);
 $("comicExport").addEventListener("click",exportSvg);
 $("comicSave").addEventListener("click",saveProject);
 $("comicLoad").addEventListener("click",loadProject);
 $("comicExportProject").addEventListener("click",exportProject);
 $("comicImportProject").addEventListener("click",()=>$("comicProjectFile").click());
 $("comicProjectFile").addEventListener("change",e=>{importProjectFile(e.target.files&&e.target.files[0]);e.target.value="";});
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
print("Comic Studio updated: storyboard, optional text/image APIs, portable JSON project import/export, SVG export.")
