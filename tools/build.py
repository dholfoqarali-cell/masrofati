#!/usr/bin/env python3
"""Build the standalone, AI-free Masrofati PWA from the v29 artifact source."""
import re, sys, pathlib

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
h = SRC.read_text(encoding="utf-8")


def rep(old, new, count=1):
    global h
    n = h.count(old)
    if n != count:
        sys.exit(f"expected {count} match(es), found {n} for: {old[:90]!r}")
    h = h.replace(old, new)


# ---- 1. head: PWA tags, drop the artifact-only meta ----
rep('<meta name="claude:viewport-fit-sides" content="cover">',
    '<meta name="theme-color" content="#0d6b55">\n'
    '<meta name="description" content="Mina utgifter / مصروفاتي - personal finance, stored only on your device">\n'
    '<link rel="manifest" href="manifest.webmanifest">\n'
    '<link rel="icon" href="icons/icon-192.png">\n'
    '<link rel="apple-touch-icon" href="icons/icon-192.png">')

# ---- 2. storage: local only, persisted in localStorage ----
start = h.index("async function init(){")
end = h.index("const uid8=")
new_init = r"""const LS_KEY='masrofati-data-v1';
function loadLocal(){
  try{
    const d=JSON.parse(localStorage.getItem(LS_KEY)||'null');
    if(d){S.tx=d.tx||[];S.bills=d.bills||[];S.ev=d.ev||[];S.goals=d.goals||[];S.splits=d.splits||[];
      if(d.settings)S.settings={currency:'SEK',budgets:{},goal:null,imports:[],...d.settings}}
  }catch(_){}
}
let _pt=null,_quotaWarned=false;
function persistNow(){
  clearTimeout(_pt);_pt=null;
  try{localStorage.setItem(LS_KEY,JSON.stringify({tx:S.tx,bills:S.bills,ev:S.ev,goals:S.goals,splits:S.splits,settings:S.settings}))}
  catch(e){if(!_quotaWarned){_quotaWarned=true;toast(L('امتلأ تخزين الجهاز. احذف بعض الصور أو انسخ نسخة احتياطية.','Enhetens lagring är full. Ta bort några bilder eller gör en säkerhetskopia.','Device storage is full. Remove some images or make a backup.'))}}
}
function persist(){clearTimeout(_pt);_pt=setTimeout(persistNow,40)}
addEventListener('pagehide',()=>{if(_pt)persistNow()});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&_pt)persistNow()});
async function init(){
  loadLocal();S.mode='local';S.ready=true;
  $('#fImgWrap').hidden=false;updateAiUi();
  render();
}
"""
h = h[:start] + new_init + h[end:]

# every mutation ends in render(); save from there
rep("  renderHero();renderCats();renderView();renderRemind();\n",
    "  renderHero();renderCats();renderView();renderRemind();\n  if(S.mode==='local'&&S.ready)persist();\n")

# ---- 3. no "temporary data" notice (data is saved on the device) ----
rep("</style>\n", "#notice{display:none!important}\n</style>\n", count=h.count("</style>\n")) if False else None
h = h.replace("[hidden]{display:none!important}\n", "[hidden]{display:none!important}\n#notice{display:none!important}\n", 1)

# ---- 4. text that mentioned Claude / AI keys ----
rep("Välj bilder, PDF-filer eller text (.txt, .csv) (faktura, kvitto, kontoutdrag). Claude läser dem och gör",
    "Välj textbaserade PDF-filer eller text (.txt, .csv) (faktura, kontoutdrag). Appen läser dem på din enhet och gör")
rep("اختر صورًا أو ملفات PDF أو نصًا (.txt أو .csv) (فاتورة، إيصال، كشف حساب). يقرؤها Claude ويحوّل",
    "اختر ملفات PDF نصية أو نصًا (.txt أو .csv) (فاتورة، كشف حساب). يقرؤها التطبيق على جهازك ويحوّل")
rep("Choose images, PDF files or text (.txt, .csv) (invoice, receipt, statement). Claude reads them and turns",
    "Choose text-based PDF files or text (.txt, .csv) (invoice, statement). The app reads them on your device and turns")
rep('<input id="impFile" type="file" multiple accept="image/*,application/pdf,.pdf,.txt,.csv,.tsv,text/plain,text/csv">',
    '<input id="impFile" type="file" multiple accept="application/pdf,.pdf,.txt,.csv,.tsv,text/plain,text/csv">')
rep('<input id="fImg" type="file" accept="image/*,application/pdf,.pdf,.txt,.csv,.tsv,text/plain,text/csv">',
    '<input id="fImg" type="file" accept="image/*">')

NOAI_AR = "قراءة الصور غير متاحة في هذه النسخة. استخدم ملف PDF نصيًا أو CSV أو TXT، أو أضف العملية يدويًا."
NOAI_SV = "Bildläsning finns inte i den här versionen. Använd en textbaserad PDF, CSV eller TXT, eller lägg till manuellt."
NOAI_EN = "Image reading is not available in this version. Use a text-based PDF, CSV or TXT file, or add the entry manually."
rep("L('لم تسمح باستخدام Claude لهذه الصفحة.','Du har inte tillåtit Claude på den här sidan.','You have not allowed Claude on this page.')",
    f"L('{NOAI_AR}','{NOAI_SV}','{NOAI_EN}')")
rep("L('قراءة الصور غير متاحة في هذه الصفحة الآن. أعد تحميل الصفحة واسمح لـ Claude عند ظهور الطلب.','Bildläsning är inte tillgänglig på sidan just nu. Ladda om sidan och tillåt Claude när du får frågan.','Image reading is not available on the page right now. Reload the page and allow Claude when asked.')",
    f"L('{NOAI_AR}','{NOAI_SV}','{NOAI_EN}')")
rep("L('قراءة الصور تحتاج مفتاح AI. ملفات PDF والنص تُقرأ على جهازك بلا ذكاء اصطناعي.','Bildläsning kräver en AI-nyckel. PDF och text läses på din enhet utan AI.','Image reading needs an AI key. PDF and text files are read on your device without AI.')",
    "L('ملفات PDF والنص تُقرأ على جهازك. قراءة الصور غير متاحة.','PDF och text läses på din enhet. Bildläsning finns inte.','PDF and text files are read on your device. Image reading is not available.')")
rep("L('لم أجد أرقامًا. قراءة الصور تحتاج مفتاح AI (زر «مفتاح AI» أعلى الصفحة)، أو اكتب القيم يدويًا.','Hittade inga siffror. Bildläsning kräver en AI-nyckel (knappen ”AI-nyckel” högst upp) eller skriv in manuellt.','No numbers found. Image reading needs an AI key (the “AI key” button at the top), or type the values.')",
    "L('لم أجد أرقامًا. اكتب القيم يدويًا.','Hittade inga siffror. Skriv in värdena manuellt.','No numbers found. Type the values manually.')")

# ---- 5. privacy policy: no AI, no API key; add "not advice" ----
def strip_section(h, title):
    pat = re.compile(r"<h2>" + re.escape(title) + r"</h2><p>.*?</p>\n", re.S)
    h2, n = pat.subn("", h, count=1)
    if n != 1:
        sys.exit("privacy section not found: " + title)
    return h2

h = strip_section(h, "قراءة الصور بالذكاء الاصطناعي (اختيارية)")
h = strip_section(h, "Läsning av bilder med AI (valfritt)")
h = strip_section(h, "Reading images with AI (optional)")

rep("<h2>قراءة الملفات</h2><p>ملفات PDF النصية وCSV وTXT تُقرأ على جهازك ولا تُرسل إلى أي جهة.</p>",
    "<h2>قراءة الملفات</h2><p>ملفات PDF النصية وCSV وTXT تُقرأ على جهازك ولا تُرسل إلى أي جهة. لا يستخدم التطبيق أي ذكاء اصطناعي ولا يرسل بياناتك إلى أي خدمة.</p>\n"
    "<h2>ليس استشارة</h2><p>النصائح والحسابات في التطبيق عامة وللتوضيح فقط، وليست استشارة مالية أو ضريبية.</p>")
rep("<h2>Läsning av filer</h2><p>Textbaserade PDF-filer, CSV och TXT läses på din enhet och skickas inte någonstans.</p>",
    "<h2>Läsning av filer</h2><p>Textbaserade PDF-filer, CSV och TXT läses på din enhet och skickas inte någonstans. Appen använder ingen AI och skickar inte dina uppgifter till någon tjänst.</p>\n"
    "<h2>Ingen rådgivning</h2><p>Råd och beräkningar i appen är allmänna och endast vägledande. De är inte finansiell rådgivning eller skatterådgivning.</p>")
rep("<h2>Reading files</h2><p>Text-based PDF, CSV and TXT files are read on your device and are not sent anywhere.</p>",
    "<h2>Reading files</h2><p>Text-based PDF, CSV and TXT files are read on your device and are not sent anywhere. The app uses no AI and sends your data to no service.</p>\n"
    "<h2>Not advice</h2><p>Tips and calculations in the app are general and for guidance only. They are not financial or tax advice.</p>")

# ---- 5b. CSV export: normal browser download instead of the artifact downloads capability ----
rep("""  try{const dl=await window.claude?.use?.('downloads');
    if(!dl){toast(L('التصدير غير متاح هنا','Export är inte tillgänglig här','Export is not available here'));return}
    await dl.save({filename:'masrofati-'+todayStr()+'.csv',data:csv});
  }catch(e){if(e&&e.code!=='declined')toast(L('تعذّر التصدير','Exporten misslyckades','The export failed'))}""",
"""  try{
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download='masrofati-'+todayStr()+'.csv';
    document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),4000);
  }catch(e){toast(L('تعذّر التصدير','Exporten misslyckades','The export failed'))}""")

# ---- 6. service worker registration ----
rep("applyStatic();render();init();routePrivacy();",
    "applyStatic();render();init();routePrivacy();\n"
    "if('serviceWorker' in navigator&&location.protocol.startsWith('http')){addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}))}")

# ---- 7. sanity: nothing AI-related left that is reachable ----
for bad in ["window.claude", "api.anthropic", "anthropic"]:
    if bad in h:
        # allowed only inside the sample-guarded code we removed; fail if present in output
        sys.exit("leftover reference: " + bad)

OUT.write_text(h, encoding="utf-8")
print("built", OUT, len(h), "bytes")
