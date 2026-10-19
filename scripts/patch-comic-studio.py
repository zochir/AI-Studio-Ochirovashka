from pathlib import Path
import re, sys

p = Path(sys.argv[1]) / "app/src/main/assets/index.html"
html = p.read_text(encoding="utf-8")
start_marker = "<!-- AI_STUDIO_COMIC_MODULE_V1 -->"
end_marker = "<!-- /AI_STUDIO_COMIC_MODULE_V1 -->"
module = r"""
<!-- AI_STUDIO_COMIC_MODULE_V1 -->
<style>
#comicLab{margin:16px auto;padding:16px;max-width:1050px;border:1px solid #cbd5e1;border-radius:16px;background:#fff;color:#172033;font:inherit}
#comicLab *{box-sizing:border-box}#comicLab label{display:block;margin:10px 0 5px;font-weight:600}
#comicLab textarea,#comicLab input,#comicLab select{display:block;width:100%;min-height:44px;padding:11px;border:1px solid #94a3b8;border-radius:10px;font:inherit}
#comicLab textarea{min-height:unset}
#comicLab .comic-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
#comicLab button{min-height:44px;padding:11px 14px;border:0;border-radius:10px;margin:8px 8px 0 0;background:#475569;color:#fff;font:inherit;font-weight:650;line-height:1.25;white-space:normal;max-width:100%}
#comicLab button:disabled{opacity:.55}
#comicLab #comicGenerate{background:#334155}
#comicLab #comicGenerateImages{background:#4338ca;width:100%;min-height:52px;font-size:1.05em}
#comicLab #comicSave,#comicLab #comicLoad{background:#0f766e}
#comicLab #comicExportProject,#comicLab #comicExport,#comicLab #comicExportPng,#comicLab #comicExportHtml{background:#64748b}
#comicLab .comic-main-actions{display:grid;grid-template-columns:1fr;gap:8px;margin-top:16px}
#comicLab .comic-main-actions button{width:100%;min-height:54px;margin:0;font-size:1.05em;text-align:left;padding:14px 16px}
#comicLab .comic-main-actions .comic-primary{background:#4338ca}
#comicLab .comic-main-actions .comic-primary-art{background:#0f766e}
#comicLab .comic-main-actions .comic-primary-save{background:#475569}
#comicLab .comic-save-project{width:100%;margin-top:8px;background:#475569}
#comicLab .comic-options{margin-top:14px}
#comicLab .comic-options summary{font-weight:650}
#comicLab .comic-secondary{background:#64748b}
#comicLab .comic-file-tools{margin-top:12px}
#comicLab .comic-file-tools button{background:#64748b}
#comicLab .comic-file-tools summary{font-weight:700}
#comicLab .comic-note{font-size:.9em;line-height:1.5;opacity:.9}
#comicLab details{margin:12px 0;padding:12px;border:1px solid #cbd5e1;border-radius:12px;background:#f8fafc}
#comicLab details summary{cursor:pointer;line-height:1.4;padding:4px 0}
#comicLab details[open]{background:#fff}
#comicLab .comic-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:16px}
@media(max-width:480px){#comicLab{padding:12px}#comicLab button{width:100%;margin-right:0}#comicLab .comic-row{grid-template-columns:1fr}}
#comicLab .comic-panel{border:2px solid #172033;border-radius:8px;background:#fff;color:#172033;overflow:hidden;box-shadow:3px 4px 0 #172033}
#comicLab .comic-art{width:100%;aspect-ratio:1/1;display:grid;place-items:center;background:#e2e8f0;color:#334155;font-size:15px;text-align:center;padding:18px;object-fit:cover}#comicLab .comic-art-placeholder{font-weight:650;line-height:1.5}
#comicLab .comic-panel h3,#comicLab .comic-panel p{margin:10px;line-height:1.4}
</style>
<section id="comicLab" aria-labelledby="comicLabTitle">
<h2 id="comicLabTitle">Комикс-студия</h2>
<p class="comic-note" style="margin-top:-6px;font-weight:650">Разработчики: Очир Зулаев и Алиса</p>
<p class="comic-note">Всего два шага: <strong>создайте раскадровку → нарисуйте кадры.</strong> Сохранение выполняется отдельно. Серый блок означает, что иллюстрации ещё нет.</p><p class="comic-note">Настройки генерации находятся ниже в разделе «Дополнительно». Скачивание модели на 1,15 ГБ не запускается автоматически.</p><p class="comic-note" role="note"><strong>Важно:</strong> APK сам по себе не содержит готовую модель для рисования. Для настоящих иллюстраций нужен внешний API с доступной квотой и ключом либо настроенный сервер ComfyUI. Запросы к внешнему генератору начинаются только после нажатия «2. Нарисовать комикс»; модель на 1,15 ГБ загружается только отдельной кнопкой.</p>
<label for="comicStory">Идея или сюжет</label><textarea id="comicStory" rows="4" placeholder="Опишите героев, место действия и события"></textarea>
<details class="comic-options"><summary>Настроить персонажей и стиль (необязательно)</summary>
<label for="comicCharacterName">Имя персонажа</label><input id="comicCharacterName" maxlength="80" placeholder="Например, Лея"><label for="comicCharacterLook">Внешность персонажа</label><textarea id="comicCharacterLook" rows="2" placeholder="Лицо, волосы, одежда, телосложение и отличительные детали"></textarea><button id="comicAddCharacter" type="button">Добавить персонажа</button><label for="comicCharacters">Персонажи и их постоянная внешность</label><textarea id="comicCharacters" rows="3" placeholder="Необязательно. Добавьте персонажей, если важно сохранять их внешность между кадрами."></textarea>
<div class="comic-row"><div><label for="comicMood">Атмосфера</label><select id="comicMood"><option>Приключение и динамика</option><option>Тёплая и уютная</option><option>Мрачная и напряжённая</option><option>Эпическая и масштабная</option><option>Юмор и лёгкость</option><option>Меланхоличная</option></select></div><div><label for="comicComposition">Композиция</label><select id="comicComposition"><option>Автоматически по сцене</option><option>Кинематографический широкий план</option><option>Портрет и эмоции</option><option>Динамичный ракурс и движение</option><option>Общий план окружения</option></select></div></div>
<div class="comic-row"><div><label for="comicCount">Количество кадров</label><select id="comicCount"><option>3</option><option selected>4</option><option>6</option><option>8</option></select></div>
<div><label for="comicStyle">Стиль рисунка</label><select id="comicStyle"><option selected>Кинематографический реализм</option><option>Комикс с чёткими контурами</option><option>Графический роман</option><option>Манга</option><option>Аниме</option><option>Акварельное фэнтези</option><option>Карандашный скетч</option><option>Ретро-комикс</option><option>Пиксель-арт</option><option>3D-анимация</option><option>Научная фантастика</option><option>Нуар</option><option>Поп-арт</option><option>Европейский альбомный комикс</option></select></div></div></details>
<details><summary style="margin-top:14px;cursor:pointer;font-weight:650">Дополнительно: ИИ-сценарист</summary>
<p class="comic-note">OpenAI-compatible Chat Completions (например, локальный Ollama /v1/chat/completions). Ответ модели должен содержать JSON-массив с полями title, scene, dialogue. Для локального сервера ключ обычно не нужен.</p>
<label for="comicEndpoint">Chat-completions endpoint</label><input id="comicEndpoint" type="url" placeholder="https://example.com/v1/chat/completions">
<label for="comicModel">Модель текста</label><input id="comicModel" placeholder="text-model">
<label for="comicKey">Ключ текстового API</label><input id="comicKey" type="password" autocomplete="off">
</details>
<details><summary style="margin-top:14px;cursor:pointer;font-weight:650">Дополнительно: внешний генератор изображений</summary>
<p class="comic-note">Есть два режима: OpenAI-compatible Images API и Pollinations. Pollinations требует API-ключ с сайта провайдера; доступность и стоимость зависят от вашей квоты и выбранной модели. Не публикуйте секретный ключ.</p><button id="comicUsePollinations" type="button">Настроить Pollinations</button><p class="comic-note">Обычный Images API: POST с model, prompt, size, n; ответ data[0].url или data[0].b64_json. Кнопка Pollinations переключает генератор на прямой image endpoint.</p>
<label for="comicImageEndpoint">Images endpoint</label><input id="comicImageEndpoint" type="url" placeholder="https://example.com/v1/images/generations">
<label for="comicImageModel">Модель изображений</label><input id="comicImageModel" placeholder="image-model">
<label for="comicImageKey">Ключ API изображений</label><input id="comicImageKey" type="password" autocomplete="off">
</details>
<details><summary style="margin-top:14px;cursor:pointer;font-weight:650">Дополнительно: генерация на телефоне / ComfyUI</summary>
<p class="comic-note">Запустите ComfyUI на своём компьютере и включите доступ из локальной сети. Вставьте API-workflow JSON из ComfyUI. В workflow укажите строку __PROMPT__ в поле positive prompt, которое нужно заменить описанием кадра. Для WebView/браузера ComfyUI должен разрешать CORS для origin приложения. Не открывайте ComfyUI в интернет без защиты.</p>
<label for="comicLocalEndpoint">Адрес локального ComfyUI</label><input id="comicLocalEndpoint" type="url" placeholder="http://192.168.1.20:8188">
<label for="comicReferenceFile">Референс внешности персонажа (необязательно)</label><input id="comicReferenceFile" type="file" accept="image/png,image/jpeg,image/webp"><p class="comic-note">До 2 МБ. Для использования референса добавьте в ComfyUI API-workflow узел Load Image и подключите его к IPAdapter или другому reference-conditioning узлу. В поле имени изображения укажите __CHARACTER_REFERENCE__. Без такого подключения изображение не влияет на результат.</p><p id="comicReferenceStatus" class="comic-note">Референс не выбран.</p><label for="comicWorkflow">API workflow JSON</label><textarea id="comicWorkflow" rows="5" placeholder='{"1":{"inputs":{"image":"__CHARACTER_REFERENCE__"}},"2":{"inputs":{"text":"__PROMPT__"}}}'></textarea>
<button id="comicCheckLocal" type="button">Проверить подключение</button><button id="comicCheckNative" type="button">Проверить локальный движок Android</button><button id="comicDownloadNativeModel" type="button">Скачать модель на телефон (≈1,15 ГБ)</button><button id="comicGenerateNative" type="button">Сгенерировать первый кадр на телефоне</button><p id="comicNativeModelProgress" class="comic-note" role="status">Локальная модель не скачивается автоматически. Для загрузки требуется свободное место и явное подтверждение.</p><button id="comicBuildWorkflow" type="button">Автособрать workflow по установленной модели</button><button id="comicGenerateLocal" type="button">Сгенерировать кадры локально</button><p class="comic-note">Автосборка использует стандартные узлы ComfyUI и первый установленный checkpoint. Это базовая генерация без IPAdapter; для жёсткого сохранения лица подключите reference-conditioning workflow.</p>
</details>
<div class="comic-main-actions" aria-label="Основные действия">
<button id="comicGenerate" class="comic-primary" type="button">1. Создать раскадровку</button>
<button id="comicGenerateImages" class="comic-primary comic-primary-art" type="button">2. Нарисовать комикс</button>
</div>
<button id="comicSave" class="comic-secondary comic-save-project" type="button">Сохранить проект</button>
<button id="comicRetryImages" class="comic-secondary" type="button" disabled>Повторить неудачные кадры</button>
<details class="comic-file-tools"><summary>Открыть проект или экспортировать</summary>
<button id="comicLoad" type="button">Открыть сохранённый проект</button>
<button id="comicExportHtml" type="button">Экспортировать готовый комикс</button>
<button id="comicExportPng" type="button">Сохранить страницу как PNG</button>
<button id="comicExport" type="button">Сохранить страницу как SVG</button>
<button id="comicExportProject" type="button">Экспорт проекта (JSON)</button>
<button id="comicImportProject" type="button">Импорт проекта (JSON)</button>
<input id="comicProjectFile" type="file" accept="application/json,.json" hidden>
</details>
<p id="comicStatus" role="status" aria-live="polite"></p><div id="comicPanels" class="comic-grid"></div>
</section>
<script>
(function(){
 const $=id=>document.getElementById(id);
 let panels=[];
 let nativeImageRequest=0;
 let nativeImageWatchdog=0;
 let nativeModelRequest=0;
 let failedImageFrames=new Set();
 let characterReferenceDataUrl="";
 const PROJECT_KEY="ai-studio-comic-project-v1";
 const nativeRoot=typeof window!=="undefined"?window:globalThis;
 nativeRoot.nativeComicImageResult=function(id,data,error){
  if(Number(id)!==nativeImageRequest)return;
  if(error){$("comicStatus").textContent="Локальная генерация не удалась: "+error;return;}
  if(!data||!String(data).startsWith("data:image/")){$("comicStatus").textContent="Движок не вернул корректное изображение.";return;}
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  panels[0].imageUrl=String(data);render(panels);$("comicStatus").textContent="Первый кадр создан локально на телефоне.";
 };
 nativeRoot.nativeComicModelProgress=function(id,percent,message,done){
  if(Number(id)!==nativeModelRequest)return;
  $("comicNativeModelProgress").textContent=(percent<0?"Ошибка загрузки: ":("Загрузка модели — "+percent+"%: "))+message;
  $("comicDownloadNativeModel").disabled=!done;
  if(done&&percent>=0)$("comicStatus").textContent="Локальная модель готова к проверке генерации.";
 };
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
 async function responseError(res,provider,frame){
  let detail="";
  try{
   const raw=await res.text();
   if(raw){
    try{
     const body=JSON.parse(raw);
     detail=body&&body.error?(typeof body.error==="string"?body.error:(body.error.message||JSON.stringify(body.error))):(body&&body.message)||raw;
    }catch(_){detail=raw;}
    detail=String(detail).replace(/\s+/g," ").trim().slice(0,320);
   }
  }catch(_){}
  return Error(provider+" вернул HTTP "+res.status+" на кадре "+frame+(detail?": "+detail:""));
 }

 function render(items){
  panels=items.map((p,i)=>({title:String(p.title||("Кадр "+(i+1))),scene:String(p.scene||p.description||""),dialogue:String(p.dialogue||""),imageUrl:p.imageUrl||""}));
  $("comicPanels").innerHTML=panels.map((p,i)=>'<article class="comic-panel">'+(p.imageUrl?'<img class="comic-art" alt="Иллюстрация кадра '+(i+1)+'" src="'+esc(p.imageUrl)+'">':'<div class="comic-art comic-art-placeholder">Иллюстрация ещё не создана<br>Настройте генератор и нажмите «Сгенерировать изображения кадров»</div>')+'<h3>Кадр '+(i+1)+' — редактирование</h3><label>Название кадра</label><input data-panel-index="'+i+'" data-panel-field="title" aria-label="Название кадра '+(i+1)+'" value="'+esc(p.title)+'"><label>Описание сцены</label><textarea data-panel-index="'+i+'" data-panel-field="scene" aria-label="Описание сцены '+(i+1)+'" rows="3">'+esc(p.scene)+'</textarea><label>Реплика</label><textarea data-panel-index="'+i+'" data-panel-field="dialogue" aria-label="Реплика кадра '+(i+1)+'" rows="2">'+esc(p.dialogue)+'</textarea></article>').join("");
  if($("comicPanels").querySelectorAll)$("comicPanels").querySelectorAll("[data-panel-index][data-panel-field]").forEach(input=>input.addEventListener("input",()=>{
   const i=Number(input.getAttribute("data-panel-index")),field=input.getAttribute("data-panel-field");
   if(panels[i]&&["title","scene","dialogue"].includes(field)){panels[i][field]=input.value;$("comicStatus").textContent="Изменения кадра "+(i+1)+" внесены. Нажмите «Сохранить проект», чтобы сохранить их на устройстве.";}
  }));
 }
 function saveProject(){
  try{
   const data={version:1,story:$("comicStory").value,characters:$("comicCharacters").value,mood:$("comicMood").value,composition:$("comicComposition").value,count:$("comicCount").value,style:$("comicStyle").value,endpoint:$("comicEndpoint").value,model:$("comicModel").value,imageEndpoint:$("comicImageEndpoint").value,imageModel:$("comicImageModel").value,localEndpoint:$("comicLocalEndpoint").value,workflow:$("comicWorkflow").value,characterReferenceDataUrl:characterReferenceDataUrl,panels:panels};
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
   characterReferenceDataUrl=String(data.characterReferenceDataUrl||"");$("comicReferenceStatus").textContent=characterReferenceDataUrl?"Референс загружен из сохранённого проекта.":"Референс не выбран.";
   failedImageFrames.clear();$("comicRetryImages").disabled=true;
   render(data.panels);
   $("comicStatus").textContent="Проект загружен ("+panels.length+" кадров).";
  }catch(e){$("comicStatus").textContent="Не удалось загрузить проект: "+e.message;}
 }
 function localScenes(story,n){
  const sentences=story.replace(/\s+/g," ").split(/[.!?。！？]+/).map(x=>x.trim()).filter(Boolean),chunks=sentences.length?sentences:[story];
  const battlePattern=/сраж|битв|бой\b|войн|арм(ия|ии|ию|ией)|осад|напад|атак|дуэл|меч|дракон|монстр|демон|враг|легион|battle|fight|warfare|army|siege|dragon|monster|demon|enemy/i;
  const battle= battlePattern.test(story);
  const beats=[
   "Масштабный установочный план: две противоборствующие стороны сходятся на поле боя, видны рельеф, погода, знамёна и масштаб угрозы.",
   "Начало штурма: стремительный рывок воинов, столкновение передних линий, летящие обломки и пыль; действие читается с первого взгляда.",
   "Ближний бой: герой отражает удар и контратакует, оружие сталкивается с искрами, выразительные позы и напряжённые лица.",
   "Перелом сражения: противник меняет тактику, рушится укрытие или защитный строй, герои вынуждены действовать вместе.",
   "Кульминационная схватка: главный герой сталкивается с сильнейшим противником на фоне масштабного хаоса битвы.",
   "Решающий манёвр: рискованный совместный удар меняет ход сражения; сохраняются направление движения и география сцены.",
   "Последствия боя: дым рассеивается, уцелевшие перегруппировываются, герои осознают цену победы.",
   "Эпический финальный план: силуэты героев на фоне поля боя и драматического неба, ощущение завершения и нового пути."
  ];
  return Array.from({length:n},(_,i)=>{
   const base=chunks[Math.min(chunks.length-1,Math.floor(i*chunks.length/n))];
   const scene=battle?base+"\nВизуальный этап сражения: "+beats[Math.min(i,beats.length-1)]:base;
   return {title:names[i]||("Сцена "+(i+1)),scene};
  });
 }
 function projectData(){
  return {format:"ai-comic-studio-project",version:1,story:$("comicStory").value,characters:$("comicCharacters").value,mood:$("comicMood").value,composition:$("comicComposition").value,count:$("comicCount").value,style:$("comicStyle").value,endpoint:$("comicEndpoint").value,model:$("comicModel").value,imageEndpoint:$("comicImageEndpoint").value,imageModel:$("comicImageModel").value,localEndpoint:$("comicLocalEndpoint").value,workflow:$("comicWorkflow").value,characterReferenceDataUrl:characterReferenceDataUrl,panels:panels.map(p=>Object.assign({},p))};
 }
 function downloadText(filename,text,mime){
  const url=URL.createObjectURL(new Blob([text],{type:mime})),a=document.createElement("a");
  a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 async function exportProject(){
  $("comicExportProject").disabled=true;$("comicStatus").textContent="Подготовка переносимого проекта: встраиваю изображения в JSON…";
  try{
   const data=projectData(),warnings=[];
   for(let i=0;i<data.panels.length;i++){
    const panel=data.panels[i],src=panel.imageUrl;
    delete panel.imageExportWarning;
    if(!src||/^data:image\//i.test(src))continue;
    try{
     const response=await fetchTimed(src,{},20000);
     if(!response.ok)throw Error("HTTP "+response.status);
     const blob=await response.blob();
     if(!blob.type||!blob.type.toLowerCase().startsWith("image/"))throw Error("ответ не является изображением");
     if(!blob.size)throw Error("пустой файл");
     if(blob.size>20*1024*1024)throw Error("файл больше лимита 20 МБ на кадр");
     const bytes=new Uint8Array(await blob.arrayBuffer());let binary="";
     for(let j=0;j<bytes.length;j+=0x8000)binary+=String.fromCharCode(...bytes.subarray(j,j+0x8000));
     panel.imageUrl="data:"+blob.type+";base64,"+btoa(binary);
    }catch(e){
     panel.imageExportWarning="Не удалось встроить изображение ("+e.message+"). Ссылка может не работать на другом устройстве.";
     warnings.push("кадр "+(i+1)+": "+e.message);
    }
   }
   downloadText("comic-project.json",JSON.stringify(data,null,2),"application/json;charset=utf-8");
   const embedded=data.panels.filter(x=>/^data:image\//i.test(x.imageUrl||"")).length,external=data.panels.filter(x=>x.imageUrl&&!/^data:image\//i.test(x.imageUrl)).length;
   $("comicStatus").textContent="Проект JSON экспортирован. Изображений встроено: "+embedded+"; внешних ссылок: "+external+". Ключи API не экспортируются."+(warnings.length?" Предупреждения: "+warnings.join("; ").slice(0,500):" Все доступные изображения перенесены внутрь файла.");
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
    characterReferenceDataUrl=String(data.characterReferenceDataUrl||"");$("comicReferenceStatus").textContent=characterReferenceDataUrl?"Референс загружен из проекта.":"Референс не выбран.";
    failedImageFrames.clear();$("comicRetryImages").disabled=true;
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
    const res=await fetchTimed(endpoint,{method:"POST",headers:Object.assign({"Content-Type":"application/json"},key?{"Authorization":"Bearer "+key}:{}),body:JSON.stringify({model:model,temperature:.7,messages:[{role:"system",content:"Верни только JSON-массив из "+n+" объектов с полями title, scene, dialogue на русском языке. Это последовательные кадры одного комикса. Сохраняй внешний вид героев, причинно-следственную связь, разнообразие планов и эмоций. Учитывай паспорт персонажей и атмосферу. Если сюжет содержит войну, битву, осаду, монстров или дуэль, построй нарастающую хореографию эпичного сражения: масштаб поля боя, столкновение сторон, ближний бой, тактический перелом, кульминационная схватка и последствия. Каждый кадр должен показывать новый конкретный момент действия, а не повторять общий план."},{role:"user",content:"Визуальный стиль: "+$("comicStyle").value+". Атмосфера: "+mood+". Композиция: "+composition+". Паспорт персонажей: "+(characters||"создай подходящих сюжету героев и сохраняй их внешний вид")+". Сюжет: "+story}]})});
    if(!res.ok)throw await responseError(res,"Текстовый API","—");
    const data=await res.json(),raw=data.choices&&data.choices[0]&&data.choices[0].message&&data.choices[0].message.content;
    if(!raw)throw Error("В ответе текстового API нет сценария.");
    const parsed=JSON.parse(String(raw).replace(/^\x60\x60\x60(?:json)?\s*/i,"").replace(/\s*\x60\x60\x60$/,""));
    if(!Array.isArray(parsed)||!parsed.length)throw Error("Ожидался JSON-массив кадров.");
    failedImageFrames.clear();$("comicRetryImages").disabled=true;
   render(parsed.slice(0,n));$("comicStatus").textContent="Сценарий создан ИИ. Следующий шаг — сгенерировать изображения кадров.";
   }else{
    failedImageFrames.clear();$("comicRetryImages").disabled=true;
    render(localScenes(story,n));$("comicStatus").textContent="Создана локальная текстовая раскадровка. Для сценария от ИИ укажите настройки текстового API.";
   }
  }catch(e){$("comicStatus").textContent="Ошибка сценария: "+e.message;}
  finally{$("comicGenerate").disabled=false;}
 }
 function stablePanelSeed(panelIndex){
  const source=String($("comicStory").value||"")+"|"+String($("comicCharacters").value||"")+"|"+String(panels[panelIndex]&&panels[panelIndex].scene||"")+"|panel:"+panelIndex;
  let hash=2166136261;
  for(let i=0;i<source.length;i++){hash^=source.charCodeAt(i);hash=Math.imul(hash,16777619);}
  return (hash>>>0)%2147483647;
 }
 async function generateImages(retryOnly=false){
  const endpoint=$("comicImageEndpoint").value.trim(),model=$("comicImageModel").value.trim(),key=$("comicImageKey").value;
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  if(!endpoint||!model){$("comicStatus").textContent="Для генерации изображений укажите endpoint и модель. Ключ нужен только если его требует сервер.";return;}
  if(!/^https?:\/\//i.test(endpoint)){$("comicStatus").textContent="Endpoint должен начинаться с http:// или https://.";return;}
  const indices=retryOnly?Array.from(failedImageFrames).sort((a,b)=>a-b):panels.map((_,i)=>i);
  if(!indices.length){$("comicStatus").textContent=retryOnly?"Нет неудачных кадров для повтора.":"В проекте нет кадров.";return;}
  const providerName=endpoint.replace(/\/$/,"")==="https://gen.pollinations.ai/image"?"Pollinations":"внешний Images API";
  const confirmationText="Будет отправлено "+indices.length+" запрос(ов) генерации в "+providerName+" — по одному на каждый кадр. Проверьте тариф и остаток квоты: запросы могут расходовать кредиты или быть платными. Продолжить?";
  if(typeof confirm==="function"&&!confirm(confirmationText)){$("comicStatus").textContent="Генерация отменена: запросы не отправлялись.";return;}
  $("comicGenerateImages").disabled=true;
  try{
   let completed=0;const failures=[];
   for(const i of indices){
    $("comicStatus").textContent=(retryOnly?"Повторная генерация кадра ":"Генерация изображения ")+(i+1)+" из "+panels.length+"…";
    try{
     const previousScene=i>0?panels[i-1].scene:"This is the opening scene; establish the setting and character appearances.";
     const nextScene=i<panels.length-1?panels[i+1].scene:"This is the final scene; visually resolve the immediate action.";
     const realismGuide=$("comicStyle").value==="Кинематографический реализм"?"Photorealistic live-action film still, believable human anatomy and facial proportions, natural skin texture with pores and subtle imperfections, physically plausible hair and fabric, realistic weathering on props, grounded materials, natural motivated lighting, cinematic exposure and color grading, realistic depth of field, documentary-level environmental detail, shot on a real cinema camera with a 35mm or 50mm lens, coherent perspective, no plastic skin, no waxy faces, no synthetic 3D-render look, no painterly brush strokes, no collage.":"Respect the selected art style while keeping anatomy, perspective, lighting, materials, expressions and environments physically convincing and highly detailed.";
     const battlePattern=/сраж|битв|бой\b|войн|арм(ия|ии|ию|ией)|осад|напад|атак|дуэл|меч|дракон|монстр|демон|враг|легион|battle|fight|warfare|army|siege|dragon|monster|demon|enemy/i;
     const battleGuide=(battlePattern.test(String($("comicStory").value)+" "+String(panels[i].scene))||$("comicMood").value==="Эпическая и масштабная")?" EPIC BATTLE DIRECTION: when this scene depicts combat, show a huge cinematic battlefield with clearly readable action choreography, opposing forces, dynamic wide-to-close visual storytelling, powerful but physically believable impacts, sparks, dust, debris, dramatic weather and volumetric light, expressive faces, distinct silhouettes, coherent weapon paths and geography. Make the combat feel consequential and grand, never static posing. Avoid gore, avoid text.":"";
     const prompt="Create one polished, high-detail sequential-story panel. Depict a specific moment in the action, not a poster, collage, icon, logo, paint palette, easel, artist tools, or placeholder. "+realismGuide+battleGuide+" No text, letters, subtitles, speech bubbles, watermark, logo, paint palette, or easel in the image. Visual style: "+$("comicStyle").value+". Mood: "+$("comicMood").value+". Composition: "+$("comicComposition").value+". Panel "+(i+1)+" of "+panels.length+". Character design bible (preserve exact face, age, body proportions, hairstyle, clothing, colors and distinguishing marks in every panel): "+($("comicCharacters").value.trim()||"derive a coherent recurring design from the story and keep it unchanged")+". Narrative continuity: previous panel: "+previousScene+". Next panel: "+nextScene+". Treat the character design bible as immutable model-sheet canon: the same exact individual must recur in every panel, with matching facial structure, eye color, skin tone, age, hairline, hairstyle, body proportions, signature marks, clothing cut and exact color palette. Never redesign, recast, age-shift, beautify, duplicate or substitute the lead character. Keep identities, costume details, props, geography, weather, lighting direction and time of day consistent unless explicitly changed by the story. If the scene changes camera angle, adapt perspective and pose only; do not alter identity or costume. Show readable physical action and believable body language, natural facial emotion, correct hands and anatomy, detailed foreground/midground/background, purposeful camera framing and no duplicated people or objects. Story moment to depict now: "+panels[i].scene+". Character/dialogue context (convey emotion visually, do not write the dialogue): "+panels[i].dialogue+". Vary shot size and camera angle to fit the scene while preserving identity. No captions or lettering. Seed for repeatable rerenders of this exact panel: "+stablePanelSeed(i)+".";
     let imageUrl="";
     if(endpoint.replace(/\/$/,"")==="https://gen.pollinations.ai/image"){
      const url=endpoint.replace(/\/$/,"")+"/"+encodeURIComponent(prompt)+"?model="+encodeURIComponent(model)+"&seed="+stablePanelSeed(i);
      const res=await fetchTimed(url,{method:"GET",headers:key?{"Authorization":"Bearer "+key}:{}},120000);
      if(!res.ok)throw await responseError(res,"Pollinations",i+1);
      const blob=await res.blob();
      if(!blob.type||!blob.type.toLowerCase().startsWith("image/")||!blob.size)throw Error("Pollinations не вернул непустое изображение для кадра "+(i+1)+" (Content-Type: "+(blob.type||"не указан")+"). Проверьте ключ, квоту и ответ провайдера.");
      const bytes=new Uint8Array(await blob.arrayBuffer());let binary="";
      for(let j=0;j<bytes.length;j+=0x8000)binary+=String.fromCharCode(...bytes.subarray(j,j+0x8000));
      imageUrl="data:"+blob.type+";base64,"+btoa(binary);
     }else{
      const res=await fetchTimed(endpoint,{method:"POST",headers:Object.assign({"Content-Type":"application/json"},key?{"Authorization":"Bearer "+key}:{}),body:JSON.stringify({model:model,prompt:prompt,size:"1024x1024",n:1,seed:stablePanelSeed(i)})},120000);
      if(!res.ok)throw await responseError(res,"Images API",i+1);
      const data=await res.json(),item=data.data&&data.data[0];
      if(!item)throw Error("Images API не вернул data[0] для кадра "+(i+1)+". Проверьте формат ответа провайдера.");
      if(item.b64_json){
       if(typeof item.b64_json!=="string"||!item.b64_json.length||!/^[A-Za-z0-9+/]+={0,2}$/.test(item.b64_json))throw Error("Images API вернул некорректные base64-данные для кадра "+(i+1)+".");
       imageUrl="data:image/png;base64,"+item.b64_json;
      }else if(item.url){
       if(typeof item.url!=="string"||!(item.url.toLowerCase().startsWith("http://")||item.url.toLowerCase().startsWith("https://")||item.url.toLowerCase().startsWith("data:image/")))throw Error("Images API вернул неподдерживаемый адрес изображения для кадра "+(i+1)+". Ожидается HTTP(S)-URL или data:image.");
       imageUrl=item.url;
      }else{
       throw Error("Images API не вернул ни url, ни b64_json для кадра "+(i+1)+".");
      }
     }
     if(!imageUrl)throw Error("Ответ кадра "+(i+1)+" не содержит изображения.");
     panels[i].imageUrl=imageUrl;failedImageFrames.delete(i);completed++;render(panels);
    }catch(frameError){failedImageFrames.add(i);failures.push("кадр "+(i+1)+": "+frameError.message);$("comicStatus").textContent="Кадр "+(i+1)+" не создан; продолжаю очередь. Готово в этом запуске "+completed+" из "+indices.length+"…";}
   }
   $("comicRetryImages").disabled=failedImageFrames.size===0;
   $("comicStatus").textContent=failures.length?"Генерация завершена частично: в этом запуске готово "+completed+" из "+indices.length+". Ошибки: "+failures.join(" | ").slice(0,900)+". Нажмите «Повторить неудачные кадры», чтобы повторить только сбойные запросы.":"Готово: в этом запуске создано "+completed+" изображений. Неудачных кадров осталось: "+failedImageFrames.size+".";
  }catch(e){$("comicStatus").textContent="Генерация изображений остановлена: "+e.message+" Проверьте совместимость API, баланс и CORS; уже готовые кадры сохранены на экране.";}
  finally{$("comicGenerateImages").disabled=false;}
 }
 async function generateNativeImages(){
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  const bridge=nativeRoot.AndroidDiffusion;
  if(!bridge||typeof bridge.generate!=="function"||typeof bridge.status!=="function"){
   $("comicStatus").textContent="Локальный генератор недоступен в этой сборке. Настройте ComfyUI или внешний генератор в разделе «Дополнительно».";return;
  }
  let state="";
  try{state=bridge.status();}catch(e){$("comicStatus").textContent="Не удалось проверить локальную модель: "+e.message;return;}
  if(state!=="MODEL_PRESENT"){
   $("comicStatus").textContent="Локальная модель на телефоне не установлена. Ничего не скачано. Откройте «Дополнительно: генерация на телефоне / ComfyUI», чтобы выбрать способ генерации. Статус: "+state;return;
  }
  $("comicGenerateImages").disabled=true;
  let completed=0;const failures=[];
  try{
   for(let i=0;i<panels.length;i++){
    $("comicStatus").textContent="Рисую на телефоне кадр "+(i+1)+" из "+panels.length+"…";
    const nativeBattlePattern=/сраж|битв|бой|войн|арм(ия|ии|ию|ией)|осад|напад|атак|дуэл|меч|дракон|монстр|демон|враг|легион|battle|fight|warfare|army|siege|dragon|monster|demon|enemy/i;
    const nativeBattleGuide=(nativeBattlePattern.test(String($("comicStory").value)+" "+String(panels[i].scene))||$("comicMood").value==="Эпическая и масштабная")?" EPIC BATTLE DIRECTION: for combat scenes, show a huge cinematic battlefield, clearly readable action choreography, opposing forces, dynamic camera framing, physically believable impacts, sparks, dust, debris, dramatic weather and volumetric light, expressive faces, distinct silhouettes, coherent weapon paths and geography. Combat must feel consequential and grand, not like static posing. Avoid gore and text.":"";
    const prompt="Create one sequential comic panel. Visual style: "+$("comicStyle").value+". Mood: "+$("comicMood").value+". Composition: "+$("comicComposition").value+". Character design bible: "+($("comicCharacters").value.trim()||"derive a coherent recurring design from the story and keep it unchanged")+". Preserve the same face, age, hairstyle, body proportions, clothing, colors and distinguishing marks. Current scene: "+panels[i].scene+". Dialogue context (show emotion only, no written text): "+panels[i].dialogue+". Story context: "+$("comicStory").value+"."+nativeBattleGuide+" Detailed, cinematic, coherent anatomy and lighting, no text, no letters, no watermark.";
    try{
     const data=await new Promise((resolve,reject)=>{
      const id=++nativeImageRequest;let settled=false;
      const finish=(err,value)=>{if(settled)return;settled=true;clearTimeout(timer);if(err)reject(err);else resolve(value);};
      const timer=setTimeout(()=>{nativeImageRequest++;finish(Error("Истекло ожидание локального движка (6 минут)."));},360000);
      nativeRoot.nativeComicImageResult=function(callbackId,imageData,error){
       if(Number(callbackId)!==id)return;
       if(error)return finish(Error(error));
       if(!imageData||!String(imageData).startsWith("data:image/png;base64,"))return finish(Error("Движок не вернул корректный PNG."));
       finish(null,String(imageData));
      };
      try{bridge.generate(prompt,String(id));}catch(e){finish(Error(e&&e.message?e.message:String(e)));}
     });
     panels[i].imageUrl=data;failedImageFrames.delete(i);completed++;render(panels);
     saveProject();
    }catch(e){failedImageFrames.add(i);failures.push("кадр "+(i+1)+": "+e.message);}
   }
   $("comicRetryImages").disabled=failedImageFrames.size===0;
   $("comicStatus").textContent=failures.length?"Локально создано "+completed+" из "+panels.length+" кадров. "+failures.join(" | ").slice(0,700)+". Повторите неудачные кадры отдельно.":"Готово: на телефоне созданы все "+completed+" кадра.";
  }finally{$("comicGenerateImages").disabled=false;}
 }
 async function buildBasicComfyWorkflow(){
  const base=$("comicLocalEndpoint").value.trim().replace(/\/$/,"");
  if(!base){$("comicStatus").textContent="Сначала укажите адрес ComfyUI.";return;}
  const button=$("comicBuildWorkflow");button.disabled=true;
  $("comicStatus").textContent="Получаю список установленных моделей ComfyUI…";
  try{
   const response=await fetchTimed(base+"/object_info/CheckpointLoaderSimple",{method:"GET"},8000);
   if(!response.ok)throw Error("HTTP "+response.status);
   const info=await response.json();
   const schema=info&&info.CheckpointLoaderSimple&&info.CheckpointLoaderSimple.input&&info.CheckpointLoaderSimple.input.required;
   const choices=schema&&schema.ckpt_name&&schema.ckpt_name[0];
   if(!Array.isArray(choices)||!choices.length)throw Error("ComfyUI не сообщил установленные checkpoint-модели. Скопируйте модель в ComfyUI/models/checkpoints и перезапустите сервер.");
   const checkpoint=String(choices[0]);
   const workflow={
    "1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":checkpoint}},
    "2":{"class_type":"CLIPTextEncode","inputs":{"text":"__PROMPT__","clip":["1",1]}},
    "3":{"class_type":"CLIPTextEncode","inputs":{"text":"low quality, low resolution, blurry, deformed anatomy, extra fingers, extra limbs, duplicate people, text, letters, watermark, logo, plastic skin, oversmoothed face","clip":["1",1]}},
    "4":{"class_type":"EmptyLatentImage","inputs":{"width":768,"height":768,"batch_size":1}},
    "5":{"class_type":"KSampler","inputs":{"seed":"__SEED__","steps":24,"cfg":6.5,"sampler_name":"euler","scheduler":"normal","denoise":1,"model":["1",0],"positive":["2",0],"negative":["3",0],"latent_image":["4",0]}},
    "6":{"class_type":"VAEDecode","inputs":{"samples":["5",0],"vae":["1",2]}},
    "7":{"class_type":"SaveImage","inputs":{"filename_prefix":"AIComicStudio","images":["6",0]}}
   };
   $("comicWorkflow").value=JSON.stringify(workflow,null,2);
   $("comicStatus").textContent="Базовый workflow создан для модели «"+checkpoint+"». Проверьте подключение и запустите локальную генерацию.";
  }catch(e){
   const reason=e&&e.name==="AbortError"?"тайм-аут (8 секунд)":e.message;
   $("comicStatus").textContent="Не удалось собрать workflow: "+reason+". Проверьте адрес, сервер и разрешение CORS.";
  }finally{button.disabled=false;}
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
 async function generateLocalImages(retryOnly=false){
  const base=$("comicLocalEndpoint").value.trim().replace(/\/$/,""),workflowText=$("comicWorkflow").value.trim();
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  if(!base||!workflowText){$("comicStatus").textContent="Укажите адрес ComfyUI и API workflow JSON.";return;}
  let template;
  try{template=JSON.parse(workflowText);}catch(e){$("comicStatus").textContent="Workflow JSON некорректен: "+e.message;return;}
  let placeholderCount=0;const countPlaceholders=v=>{if(typeof v==="string"){const m=v.match(/__PROMPT__/g);placeholderCount+=m?m.length:0;}else if(Array.isArray(v))v.forEach(countPlaceholders);else if(v&&typeof v==="object")Object.values(v).forEach(countPlaceholders);};countPlaceholders(template);
  if(!placeholderCount){$("comicStatus").textContent="Workflow не содержит __PROMPT__. Добавьте этот маркер в positive prompt API-workflow, иначе каждый кадр будет генерироваться по одному и тому же запросу.";return;}
  let referenceMarker=false;const findReference=v=>{if(typeof v==="string"&&v.includes("__CHARACTER_REFERENCE__"))referenceMarker=true;else if(Array.isArray(v))v.forEach(findReference);else if(v&&typeof v==="object")Object.values(v).forEach(findReference);};findReference(template);
  if(referenceMarker&&!characterReferenceDataUrl){$("comicStatus").textContent="Workflow содержит __CHARACTER_REFERENCE__, но файл референса не выбран.";return;}
  const indices=retryOnly?Array.from(failedImageFrames).sort((a,b)=>a-b):panels.map((_,i)=>i);
  if(!indices.length){$("comicStatus").textContent=retryOnly?"Нет неудачных локальных кадров для повтора.":"В проекте нет кадров.";return;}
  let uploadedReference="";
  if(referenceMarker){
   try{const referenceBlob=await (await fetch(characterReferenceDataUrl)).blob();const form=new FormData();form.append("image",referenceBlob,"character-reference.png");form.append("overwrite","true");form.append("type","input");const upload=await fetchTimed(base+"/upload/image",{method:"POST",body:form});if(!upload.ok)throw Error("ComfyUI /upload/image HTTP "+upload.status);const result=await upload.json();if(!result.name)throw Error("ComfyUI не вернул имя загруженного референса.");uploadedReference=(result.subfolder?result.subfolder+"/":"")+result.name;}catch(e){$("comicStatus").textContent="Не удалось загрузить референс в ComfyUI: "+e.message;return;}
  }
  $("comicGenerateLocal").disabled=true;$("comicRetryImages").disabled=true;
  let completed=0;const failures=[];
  try{
   for(const i of indices){
    $("comicStatus").textContent=(retryOnly?"Повтор локального кадра ":"Локальная генерация: отправка кадра ")+(i+1)+" из "+panels.length+"…";
    try{
     const previousScene=i>0?panels[i-1].scene:"Opening shot; establish setting and character appearances.";
     const nextScene=i<panels.length-1?panels[i+1].scene:"Final shot; visually resolve the action.";
     const realismGuide=$("comicStyle").value==="Кинематографический реализм"?"Photorealistic live-action film still, believable anatomy and facial proportions, natural skin texture with pores and subtle imperfections, physically plausible hair and fabric, grounded materials and realistic weathering, motivated cinematic lighting, natural color grading, realistic depth of field, cinema-camera perspective with a 35mm or 50mm lens, no plastic skin, waxy faces, synthetic 3D look, painterly strokes or collage.":"Respect the selected art style while maintaining convincing anatomy, perspective, lighting, materials, expressions and detailed environments.";
     const prompt="Create one polished sequential-story comic panel depicting a specific moment in action, not a poster or collage. "+realismGuide+" No text, letters, subtitles, speech bubbles, watermark, logo, paint palette or easel. Style: "+$("comicStyle").value+". Mood: "+$("comicMood").value+". Composition: "+$("comicComposition").value+". Panel "+(i+1)+" of "+panels.length+". Character design bible: preserve exact faces, ages, proportions, hairstyles, clothing, colors and distinguishing marks: "+($("comicCharacters").value.trim()||"derive coherent recurring designs and keep them unchanged")+". Continuity: previous scene: "+previousScene+". Next scene: "+nextScene+". Keep identities, costume details, props, geography, weather, lighting direction and time of day consistent unless the story explicitly changes them. Show readable physical action, believable body language, natural facial emotion, correct hands and anatomy, detailed foreground/midground/background, purposeful camera framing and no duplicated people or objects. Current scene: "+panels[i].scene+". Dialogue context (convey visually, do not render text): "+panels[i].dialogue+". Vary shot size and angle while preserving character identity. No captions or lettering.";
     const panelSeed=stablePanelSeed(i);const replace=(v)=>typeof v==="string"?(v==="__SEED__"?panelSeed:v.replace(/__PROMPT__/g,prompt).replace(/__SEED__/g,String(panelSeed)).replace(/__CHARACTER_REFERENCE__/g,uploadedReference)):Array.isArray(v)?v.map(replace):v&&typeof v==="object"?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,replace(x)])):v;
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
     const viewUrl=base+"/view?"+q.toString();
     const imageResponse=await fetchTimed(viewUrl,{},30000);
     if(!imageResponse.ok)throw Error("ComfyUI /view HTTP "+imageResponse.status+"; не удалось получить файл кадра.");
     const imageBlob=await imageResponse.blob();
     if(!imageBlob.type||!imageBlob.type.toLowerCase().startsWith("image/")||!imageBlob.size)throw Error("ComfyUI /view не вернул непустое изображение.");
     if(imageBlob.size>20*1024*1024)throw Error("Изображение больше лимита 20 МБ.");
     const imageBytes=new Uint8Array(await imageBlob.arrayBuffer());let imageBinary="";
     for(let j=0;j<imageBytes.length;j+=0x8000)imageBinary+=String.fromCharCode(...imageBytes.subarray(j,j+0x8000));
     panels[i].imageUrl="data:"+imageBlob.type+";base64,"+btoa(imageBinary);failedImageFrames.delete(i);completed++;render(panels);
    }catch(frameError){failedImageFrames.add(i);failures.push("кадр "+(i+1)+": "+frameError.message);$("comicStatus").textContent="Кадр "+(i+1)+" не создан; продолжаю локальную очередь. Готово "+completed+" из "+panels.length+"…";}
   }
   $("comicRetryImages").disabled=failedImageFrames.size===0;
   $("comicStatus").textContent=failures.length?"Локальная генерация завершена частично: готово "+completed+" из "+indices.length+" в этом запуске. Ошибки: "+failures.join(" | ").slice(0,900)+". Уже созданные изображения сохранены; повторите только неудачные кадры.":(retryOnly?"Повтор локальных кадров завершён: создано "+completed+". Неудачных кадров осталось: 0.":"ComfyUI завершил генерацию всех "+panels.length+" кадров.");
  }catch(e){$("comicStatus").textContent="Локальная генерация не завершена: "+e.message+" Проверьте, что ComfyUI запущен и workflow API-формата корректен.";}
  finally{$("comicGenerateLocal").disabled=false;$("comicRetryImages").disabled=failedImageFrames.size===0;}
 }
 function wrapSvgLines(value,maxChars,maxLines){
  const words=String(value||"").replace(/\s+/g," ").trim().split(" ").filter(Boolean),lines=[];let line="";
  for(const word of words){
   const next=line?line+" "+word:word;
   if(next.length>maxChars&&line){lines.push(line);line=word;}else line=next;
  }
  if(line)lines.push(line);
  if(lines.length>maxLines){lines.length=maxLines;lines[maxLines-1]=lines[maxLines-1].slice(0,Math.max(0,maxChars-1))+"…";}
  return lines;
 }
 function svgTextLines(lines,x,y,lineHeight,attributes){
  return '<text x="'+x+'" y="'+y+'" '+(attributes||'')+'>'+lines.map((line,i)=>'<tspan x="'+x+'" dy="'+(i===0?0:lineHeight)+'">'+escSvg(line)+'</tspan>').join("")+'</text>';
 }
 function escSvg(value){return String(value).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&apos;");}
 async function exportHtml(){
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  const button=$("comicExportHtml");button.disabled=true;
  $("comicStatus").textContent="Создаю автономный HTML-комикс: встраиваю изображения…";
  try{
   const imageData=async src=>{
    if(!src)return "";
    if(/^data:image\//i.test(src))return src;
    const response=await fetchTimed(src,{},20000);
    if(!response.ok)throw Error("HTTP "+response.status);
    const blob=await response.blob();
    if(!blob.type||!blob.type.toLowerCase().startsWith("image/")||!blob.size)throw Error("источник не вернул непустое изображение");
    if(blob.size>20*1024*1024)throw Error("изображение превышает 20 МБ");
    const bytes=new Uint8Array(await blob.arrayBuffer());let binary="";
    for(let j=0;j<bytes.length;j+=0x8000)binary+=String.fromCharCode(...bytes.subarray(j,j+0x8000));
    return "data:"+blob.type+";base64,"+btoa(binary);
   };
   const images=await Promise.all(panels.map(async(p,i)=>{try{return await imageData(p.imageUrl);}catch(e){return "";}}));
   const cards=panels.map((p,i)=>{
    const art=images[i]?'<img src="'+esc(images[i])+'" alt="Иллюстрация кадра '+(i+1)+'">':'<div class="placeholder">Иллюстрация не встроена'+(p.imageUrl?' — исходная ссылка недоступна':' — кадр ещё не сгенерирован')+'</div>';
    return '<article class="panel"><div class="art">'+art+'</div><div class="copy"><div class="number">КАДР '+(i+1)+' / '+panels.length+'</div><h2>'+esc(p.title||("Кадр "+(i+1)))+'</h2><p>'+esc(p.scene||"").replace(/\n/g,"<br>")+'</p>'+(p.dialogue?'<blockquote>'+esc(p.dialogue).replace(/\n/g,"<br>")+'</blockquote>':'')+'</div></article>';
   }).join("\n");
   const title=String($("comicStory").value.trim()||"Мой комикс").slice(0,180);
   const doc='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>html{background:#e8edf4;color:#182235;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}body{margin:0}.toolbar{position:sticky;top:0;z-index:10;display:flex;justify-content:center;gap:12px;padding:12px;background:#182235}.toolbar button{border:0;border-radius:8px;padding:12px 18px;font:inherit;font-weight:700;cursor:pointer;background:#fff;color:#182235}.book{max-width:900px;margin:0 auto;padding:24px}.cover{padding:28px 24px;background:#182235;color:#fff;border-radius:14px;margin-bottom:22px}.cover h1{margin:0 0 10px;font-size:clamp(1.8rem,5vw,3rem)}.cover p{white-space:pre-wrap;line-height:1.5}.panel{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);background:#fff;border:2px solid #182235;border-radius:12px;overflow:hidden;margin:0 0 20px;break-inside:avoid;box-shadow:4px 5px 0 #182235}.art{min-height:240px;background:#dce4ee;display:flex;align-items:center;justify-content:center}.art img{display:block;width:100%;height:100%;max-height:440px;object-fit:contain}.placeholder{padding:24px;text-align:center;color:#475569}.copy{padding:20px;align-self:center}.number{font-size:.75rem;letter-spacing:.12em;font-weight:800;color:#596579}h2{margin:.5rem 0;font-size:1.45rem}p{line-height:1.55;white-space:pre-wrap}blockquote{margin:16px 0 0;padding:12px 14px;border-left:4px solid #4f46e5;background:#eef2ff;white-space:pre-wrap;line-height:1.5;font-weight:600}.footer{color:#596579;text-align:center;font-size:.85rem;padding:16px}@media(max-width:620px){.book{padding:12px}.panel{grid-template-columns:1fr}.art{min-height:180px}.art img{max-height:340px}.copy{padding:15px}}@media print{html{background:#fff}.toolbar{display:none!important}.book{max-width:none;padding:0}.cover{background:#fff;color:#182235;border:2px solid #182235;margin-bottom:12px}.panel{box-shadow:none;margin-bottom:12px;break-inside:avoid;page-break-inside:avoid}.art{min-height:180px}.art img{max-height:280px}.footer{display:none}@page{margin:12mm}}</style></head><body><nav class="toolbar"><button type="button" onclick="window.print()">Печать / сохранить в PDF</button></nav><main class="book"><header class="cover"><h1>'+esc(title)+'</h1><p>'+esc($("comicCharacters").value||"")+'</p></header>'+cards+'<div class="footer">Автономный экспорт AI Comic Studio · изображения встроены в файл, если были доступны</div></main></body></html>';
   downloadText("comic-reader.html",doc,"text/html;charset=utf-8");
   const embedded=images.filter(Boolean).length;
   $("comicStatus").textContent="Автономный HTML-комикс экспортирован. Встроено изображений: "+embedded+" из "+panels.length+". Файл можно открыть в браузере и распечатать в PDF."+(embedded<panels.filter(p=>p.imageUrl).length?" Часть изображений недоступна из-за CORS или размера; для них добавлены заглушки.":"");
  }catch(e){$("comicStatus").textContent="Не удалось экспортировать HTML-комикс: "+e.message;}
  finally{button.disabled=false;}
 }
 async function exportSvg(format){
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
  $("comicExport").disabled=true;$("comicExportPng").disabled=true;
  $("comicStatus").textContent="Подготовка экспорта: встраиваем доступные изображения…";
  try{
   const w=400,h=250,cols=2,rows=Math.ceil(panels.length/cols),images=await Promise.all(panels.map(p=>imageData(p.imageUrl)));
   const body=panels.map((p,i)=>{
    const x=(i%cols)*w+8,y=Math.floor(i/cols)*h+8;
    const art=images[i]?'<image x="8" y="8" width="368" height="100" preserveAspectRatio="xMidYMid meet" href="'+images[i]+'"/>':'<rect x="8" y="8" width="368" height="100" fill="#e2e8f0"/><text x="192" y="48" font-size="15" text-anchor="middle" fill="#334155">Иллюстрация не создана</text>';
    const title=svgTextLines(wrapSvgLines((i+1)+". "+(p.title||"Кадр"),38,1),14,132,19,'font-size="17" font-weight="bold"');
    const scene=svgTextLines(wrapSvgLines(p.scene,48,3),14,153,16,'font-size="12" fill="#172033"');
    const dialogue=p.dialogue?svgTextLines(wrapSvgLines("Реплика: "+p.dialogue,48,2),14,scene?153+wrapSvgLines(p.scene,48,3).length*16:153,15,'font-size="11" fill="#334155"'): "";
    return '<g transform="translate('+x+' '+y+')"><rect width="384" height="234" rx="8" fill="#fff" stroke="#172033" stroke-width="3"/>'+art+title+scene+dialogue+'</g>';
   }).join("");
   const svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+(cols*w)+'" height="'+(rows*h)+'" viewBox="0 0 '+(cols*w)+' '+(rows*h)+'">'+body+'</svg>';
   const url=URL.createObjectURL(new Blob([svg],{type:"image/svg+xml;charset=utf-8"}));
   if(format==="png"){
    const rasterize=()=>new Promise((resolve,reject)=>{
     const image=new Image();
     image.onload=()=>{
      try{
       const canvas=document.createElement("canvas");canvas.width=cols*w;canvas.height=rows*h;
       const ctx=canvas.getContext("2d");if(!ctx)throw Error("Canvas 2D недоступен");
       ctx.fillStyle="#ffffff";ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(image,0,0,canvas.width,canvas.height);
       canvas.toBlob(blob=>blob?resolve(blob):reject(Error("Браузер не смог сформировать PNG")),"image/png");
      }catch(e){reject(e);}
     };
     image.onerror=()=>reject(Error("Не удалось преобразовать SVG в PNG"));
     image.src=url;
    });
    try{
     const png=await rasterize(),pngUrl=URL.createObjectURL(png),a=document.createElement("a");
     a.href=pngUrl;a.download="comic-storyboard.png";a.click();setTimeout(()=>URL.revokeObjectURL(pngUrl),1000);
    }finally{setTimeout(()=>URL.revokeObjectURL(url),1000);}
   }else{
    const a=document.createElement("a");a.href=url;a.download="comic-storyboard.svg";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
   }
   const embedded=images.filter(Boolean).length;
   $("comicStatus").textContent="Экспорт "+(format==="png"?"PNG":"SVG")+" подготовлен. Встроено изображений: "+embedded+" из "+panels.length+". Если локальный сервер блокирует CORS, соответствующий кадр экспортирован как заглушка.";
  }catch(e){$("comicStatus").textContent="Не удалось экспортировать комикс: "+e.message;}
  finally{$("comicExport").disabled=false;$("comicExportPng").disabled=false;}
 }
 $("comicReferenceFile").addEventListener("change",()=>{
  const file=$("comicReferenceFile").files&&$("comicReferenceFile").files[0];if(!file){characterReferenceDataUrl="";$("comicReferenceStatus").textContent="Референс не выбран.";return;}
  if(!/^image\/(png|jpeg|webp)$/i.test(file.type)){$("comicReferenceStatus").textContent="Поддерживаются PNG, JPEG и WebP.";return;}
  if(file.size>2*1024*1024){$("comicReferenceStatus").textContent="Файл больше 2 МБ. Уменьшите изображение и выберите снова.";return;}
  const reader=new FileReader();reader.onload=()=>{characterReferenceDataUrl=String(reader.result||"");$("comicReferenceStatus").textContent="Референс загружен ("+Math.round(file.size/1024)+" КБ). Для использования нужен workflow с reference-conditioning.";};reader.onerror=()=>{$("comicReferenceStatus").textContent="Не удалось прочитать изображение.";};reader.readAsDataURL(file);
 });
 $("comicAddCharacter").addEventListener("click",()=>{const name=$("comicCharacterName").value.trim(),look=$("comicCharacterLook").value.trim();if(!name||!look){$("comicStatus").textContent="Для карточки персонажа укажите имя и описание внешности.";return;}const card=name+" — "+look;const current=$("comicCharacters").value.trim();if(current.split("\n").some(line=>line.trim().toLocaleLowerCase()===card.toLocaleLowerCase())){$("comicStatus").textContent="Такая карточка уже добавлена.";return;}$("comicCharacters").value=current?current+"\n"+card:card;$("comicCharacterName").value="";$("comicCharacterLook").value="";$("comicStatus").textContent="Карточка персонажа «"+name+"» добавлена. Описание будет учитываться при генерации кадров.";});
 $("comicGenerate").addEventListener("click",generateScript);
 $("comicGenerateImages").addEventListener("click",()=>{let nativeStatus="";try{if(nativeRoot.AndroidDiffusion&&typeof nativeRoot.AndroidDiffusion.status==="function")nativeStatus=nativeRoot.AndroidDiffusion.status();}catch(e){nativeStatus="STATUS_ERROR";}if(nativeStatus==="MODEL_PRESENT")return generateNativeImages();if($("comicLocalEndpoint").value.trim()&&$("comicWorkflow").value.trim())return generateLocalImages(false);if($("comicImageEndpoint").value.trim()&&$("comicImageModel").value.trim())return generateImages(false);if(nativeStatus)return $("comicStatus").textContent="Локальная модель на телефоне не установлена или недоступна ("+nativeStatus+"). Ничего не скачано. Откройте «Дополнительно» и выберите ComfyUI или внешний генератор.";generateImages(false);});
 $("comicRetryImages").addEventListener("click",()=>{if($("comicLocalEndpoint").value.trim()&&$("comicWorkflow").value.trim())return generateLocalImages(true);return generateImages(true);});
 $("comicUsePollinations").addEventListener("click",()=>{$("comicImageEndpoint").value="https://gen.pollinations.ai/image/";$("comicImageModel").value="flux";$("comicStatus").textContent="Pollinations настроен. Введите API-ключ провайдера и учитывайте лимиты/стоимость выбранной модели.";});
 $("comicCheckLocal").addEventListener("click",checkLocalConnection);
 $("comicCheckNative").addEventListener("click",()=>{if(!nativeRoot.AndroidDiffusion||typeof nativeRoot.AndroidDiffusion.status!=="function"){$("comicStatus").textContent="Нативный движок не подключён в этой сборке Android.";return;}const state=nativeRoot.AndroidDiffusion.status();$("comicStatus").textContent=state==="MODEL_PRESENT"?"Файлы локальной модели найдены. Можно переходить к проверке реальной генерации.":state.startsWith("MODEL_MISSING:")?"Локальный движок собран, но модель не установлена. Не хватает файлов: "+state.slice("MODEL_MISSING:".length)+". Загрузка модели будет отдельным действием с показом размера.":"Статус локального движка: "+state;});
 $("comicDownloadNativeModel").addEventListener("click",()=>{
  if(!nativeRoot.AndroidDiffusion||typeof nativeRoot.AndroidDiffusion.downloadModel!=="function"){$("comicNativeModelProgress").textContent="Нативный движок отсутствует в этой сборке.";return;}
  if(typeof confirm!=="function"||!confirm("Скачать на телефон модель Stable Diffusion размером около 1,15 ГБ? Нужен Wi-Fi или безлимитный интернет и дополнительное свободное место. Загрузка начнётся только после подтверждения."))return;
  const id=++nativeModelRequest;$("comicDownloadNativeModel").disabled=true;$("comicNativeModelProgress").textContent="Подключение к репозиторию модели…";
  nativeRoot.AndroidDiffusion.downloadModel(String(id));
 });
 $("comicGenerateNative").addEventListener("click",()=>{
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  if(!nativeRoot.AndroidDiffusion||typeof nativeRoot.AndroidDiffusion.generate!=="function"){$("comicStatus").textContent="Нативный движок не подключён в этой сборке Android.";return;}
  const state=nativeRoot.AndroidDiffusion.status();
  if(state!=="MODEL_PRESENT"){$("comicStatus").textContent="Сначала скачайте модель. Статус: "+state;return;}
  const prompt=[panels[0].scene,$("comicCharacters").value,$("comicStyle").value,$("comicMood").value,"cinematic composition, detailed, coherent character appearance, no text, no watermark"].filter(Boolean).join(", ");
  const id=++nativeImageRequest;$("comicGenerateNative").disabled=true;$("comicStatus").textContent="Генерация первого кадра на телефоне. Это может занять несколько минут.";
  clearTimeout(nativeImageWatchdog);
  nativeRoot.nativeComicImageResult=function(callbackId,data,error){
   if(Number(callbackId)!==nativeImageRequest)return;
   clearTimeout(nativeImageWatchdog);nativeImageWatchdog=0;
   $("comicGenerateNative").disabled=false;
   if(error){$("comicStatus").textContent="Локальная генерация не удалась: "+error;return;}
   if(!data||!String(data).startsWith("data:image/png;base64,")){$("comicStatus").textContent="Движок не вернул корректный PNG.";return;}
   if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
   panels[0].imageUrl=String(data);render(panels);$("comicStatus").textContent="Первый кадр создан локально на телефоне.";
  };
  // Native inference can stall on unsupported model/runtime combinations. Restore the UI
  // after six minutes and invalidate late callbacks; this does not claim to cancel JNI work.
  nativeImageWatchdog=setTimeout(()=>{
   if(id!==nativeImageRequest)return;
   nativeImageRequest++;nativeImageWatchdog=0;$("comicGenerateNative").disabled=false;
   $("comicStatus").textContent="Локальная генерация не ответила за 6 минут. Поздний ответ будет проигнорирован; проверьте совместимость модели и движка.";
  },360000);
  try{nativeRoot.AndroidDiffusion.generate(prompt,String(id));}
  catch(error){clearTimeout(nativeImageWatchdog);nativeImageWatchdog=0;$("comicGenerateNative").disabled=false;$("comicStatus").textContent="Не удалось запустить локальную генерацию: "+(error&&error.message?error.message:String(error));}
 });
 $("comicBuildWorkflow").addEventListener("click",buildBasicComfyWorkflow);
 $("comicGenerateLocal").addEventListener("click",()=>generateLocalImages(false));
 $("comicExport").addEventListener("click",()=>exportSvg("svg"));
 $("comicExportPng").addEventListener("click",()=>exportSvg("png"));
 $("comicExportHtml").addEventListener("click",exportHtml);
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

# Add the native bridge only to the extracted Android host, never to the HTML preview.
activity = Path(sys.argv[1]) / "app/src/main/java/com/ainewsstudio/app/MainActivity.kt"
bridge_source = Path(sys.argv[1]) / "app/src/main/java/com/ainewsstudio/app/AndroidDiffusionBridge.kt"
if activity.is_file() and bridge_source.is_file():
    source = activity.read_text(encoding="utf-8")
    host_hook = 'webView.addJavascriptInterface(AndroidTtsBridge(), "AndroidTTS")'
    bridge_hook = 'webView.addJavascriptInterface(AndroidDiffusionBridge(this, webView), "AndroidDiffusion")'
    if bridge_hook not in source:
        if host_hook not in source:
            raise SystemExit("Could not locate AndroidTTS JavaScript interface hook")
        source = source.replace(host_hook, host_hook + "\n        " + bridge_hook, 1)
        activity.write_text(source, encoding="utf-8")
else:
    print("Native MNN bridge source not present in this build; AndroidDiffusion UI will report unavailable.")


manifest = Path(sys.argv[1]) / "app/src/main/AndroidManifest.xml"
if manifest.is_file():
    source = manifest.read_text(encoding="utf-8")
    permission = '<uses-permission android:name="android.permission.INTERNET" />'
    if permission not in source:
        source = re.sub(r'(<manifest\b[^>]*>)', lambda m: m.group(1) + "\n    " + permission, source, count=1)
        manifest.write_text(source, encoding="utf-8")

print("Comic Studio updated: storyboard, optional text/image APIs, native MNN model download, status and image generation bridge, portable project import/export and SVG/PNG export.")
