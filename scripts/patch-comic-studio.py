from pathlib import Path
import sys
p=Path(sys.argv[1])/"app/src/main/assets/index.html"
s=p.read_text(encoding="utf-8")
if "AI_STUDIO_COMIC_MODULE_V1" in s: raise SystemExit(0)
module = """
<!-- AI_STUDIO_COMIC_MODULE_V1 -->
<section id="comicLab" style="margin:20px;padding:18px;border:1px solid #94a3b8;border-radius:12px;background:#fff;color:#172033">
<h2>Комикс-студия</h2>
<p>Локальная текстовая раскадровка. Генерация изображений ИИ пока не подключена.</p>
<label>Сюжет <textarea id="comicStory" rows="4" style="display:block;width:100%;margin:8px 0"></textarea></label>
<label>Кадры <select id="comicCount"><option>3</option><option selected>4</option><option>6</option><option>8</option></select></label>
<details><summary style="margin-top:12px;cursor:pointer">Настройки ИИ API (необязательно)</summary>
<p style="font-size:.9em;opacity:.8">Поддерживается совместимый с OpenAI chat-completions endpoint. API-ключ хранится только в памяти страницы. CORS может блокировать прямые запросы. Это создаёт текст сценария, не изображения.</p>
<label>API endpoint <input id="comicEndpoint" type="url" placeholder="https://example.com/v1/chat/completions" style="display:block;width:100%"></label>
<label>Модель <input id="comicModel" placeholder="model-name" style="display:block;width:100%"></label>
<label>API key <input id="comicKey" type="password" autocomplete="off" style="display:block;width:100%"></label>
</details>
<button id="comicGenerate" type="button">Создать раскадровку</button>
<button id="comicExport" type="button">Экспорт SVG</button>
<p id="comicStatus" role="status"></p><div id="comicPanels" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px"></div>
</section>
<script>
(function(){
 const $=id=>document.getElementById(id); let panels=[];
 const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
 function render(items){panels=items;$("comicPanels").innerHTML=items.map((p,i)=>'<article style="border:2px solid #172033;padding:10px;background:#fff;color:#172033"><div style="height:80px;background:#dbeafe;display:grid;place-items:center;font-size:32px">🎨</div><h3>'+esc((i+1)+". "+p.title)+'</h3><p>'+esc(p.scene)+'</p></article>').join("");}
 $("comicGenerate").addEventListener("click",async function(){
  const story=$("comicStory").value.trim(),n=Number($("comicCount").value),endpoint=$("comicEndpoint")?$("comicEndpoint").value.trim():"",model=$("comicModel")?$("comicModel").value.trim():"",key=$("comicKey")?$("comicKey").value:"";
  if(!story){$("comicStatus").textContent="Введите сюжет.";return;}
  $("comicGenerate").disabled=true;
  try{
   if(endpoint){
    if(!/^https?:\\/\\//i.test(endpoint)||!model||!key)throw Error("Укажите endpoint, модель и API key.");
    const res=await fetch(endpoint,{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},body:JSON.stringify({model:model,temperature:.7,messages:[{role:"system",content:"Верни только JSON-массив из "+n+" объектов с полями title, scene, dialogue на русском языке. Это последовательные кадры комикса."},{role:"user",content:"Сюжет: "+story}]})});
    if(!res.ok)throw Error("API вернул HTTP "+res.status);
    const data=await res.json(),raw=data.choices&&data.choices[0]&&data.choices[0].message&&data.choices[0].message.content;
    if(!raw)throw Error("Ответ API не содержит сценария.");
    const parsed=JSON.parse(String(raw).replace(/^\x60\x60\x60(?:json)?\\s*/i,"").replace(/\\s*\x60\x60\x60$/,""));
    if(!Array.isArray(parsed)||!parsed.length)throw Error("Ожидался JSON-массив кадров.");
    render(parsed.slice(0,n));$("comicStatus").textContent="Сценарий создан через ИИ API. Кадры текстовые; генерация изображений не подключена.";
   }else{
    const sentences=story.replace(/\\s+/g," ").split(/[.!?。！？]+/).map(x=>x.trim()).filter(Boolean),chunks=sentences.length?sentences:[story];
    render(Array.from({length:n},(_,i)=>({title:["Завязка","Открытие","Развитие","Поворот","Кульминация","Развязка","Финал","Эпилог"][i]||("Сцена "+(i+1)),scene:chunks[Math.min(chunks.length-1,Math.floor(i*chunks.length/n))]})));
    $("comicStatus").textContent="Раскадровка создана локально. Для сценария от ИИ укажите настройки API.";
   }
  }catch(e){$("comicStatus").textContent="Не удалось создать раскадровку: "+e.message;}
  finally{$("comicGenerate").disabled=false;}
 });
 $("comicExport").addEventListener("click",function(){
  if(!panels.length){$("comicStatus").textContent="Сначала создайте раскадровку.";return;}
  const x=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  const body=panels.map((p,i)=>'<g transform="translate(10 '+(10+i*190)+')"><rect width="580" height="175" fill="white" stroke="#172033" stroke-width="3"/><text x="15" y="35" font-size="20">'+x(p.title)+'</text><foreignObject x="15" y="50" width="550" height="115"><div xmlns="http://www.w3.org/1999/xhtml" style="font:16px sans-serif">'+x(p.scene)+'</div></foreignObject></g>').join("");
  const svg='<svg xmlns="http://www.w3.org/2000/svg" width="600" height="'+(panels.length*190+20)+'">'+body+'</svg>';
  const url=URL.createObjectURL(new Blob([svg],{type:"image/svg+xml"})),a=document.createElement("a");a.href=url;a.download="comic-storyboard.svg";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 });
})();
</script>
"""
s=s.replace("</body>",module+"</body>")
p.write_text(s,encoding="utf-8")
print("Comic Studio injected")
