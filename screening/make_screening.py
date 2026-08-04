#!/usr/bin/env python3
"""Generate screening.html: a static one-page tool to hand-screen all 700
EgoProactive videos (keep / unsure / drop by suitability for multi-granularity
segmentation). Reads ONLY tool/wearable_ai_2026_egoproactive_val_700.jsonl.
Decisions live in the browser's localStorage and export to
screening_decisions.json -- nothing is written server-side.

Usage:  python3 make_screening.py   ->   writes ./screening.html
"""
import json, os, statistics
from collections import Counter
ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
JSONL = os.path.join(REPO, "tool", "wearable_ai_2026_egoproactive_val_700.jsonl")
VIDEOS = os.path.join(REPO, "videos")   # repo-root videos/ (one level up); may be absent

rows = [json.loads(l) for l in open(JSONL)]
taskcount = Counter(r["task"] for r in rows)
data = []
for i, r in enumerate(rows):
    vp = r["video_path"]
    dl = os.path.isfile(os.path.join(VIDEOS, vp))
    data.append({"i": i+1, "vp": vp, "dom": r.get("domain",""), "task": r.get("task",""),
                 "dur": r.get("duration_in_sec",0), "q": r.get("query",""),
                 "ni": len(r.get("video_intervals",[])), "dl": dl, "dup": taskcount[r["task"]]})
doms = Counter(d["dom"] for d in data); durs = sorted(d["dur"] for d in data)
def bucket(x):
    for lo,hi in [(0,60),(60,120),(120,180),(180,240)]:
        if lo<=x<hi: return f"{lo}-{hi}s"
    return "240s+"
bk = Counter(bucket(d["dur"]) for d in data)
stats = {"n": len(data), "downloaded": sum(1 for d in data if d["dl"]),
         "domains": dict(sorted(doms.items(), key=lambda x:-x[1])),
         "dur_min": durs[0], "dur_med": statistics.median(durs), "dur_max": durs[-1],
         "dur_buckets": {k: bk[k] for k in ["0-60s","60-120s","120-180s","180-240s","240s+"]},
         "uniq_tasks": len(taskcount), "dup_tasks": sum(1 for c in taskcount.values() if c>1),
         "vids_in_dup_tasks": sum(c for c in taskcount.values() if c>1),
         "max_vids_per_task": max(taskcount.values())}
DATA = json.dumps(data, ensure_ascii=False); STATS = json.dumps(stats, ensure_ascii=False)
domopts = "".join(f'<option value="{d}">{d} ({c})</option>' for d,c in stats["domains"].items())

TEMPLATE = r'''<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>EgoProactive screening — 700 videos</title>
<style>
:root{--bg:#f5f7fa;--panel:#fff;--ink:#1a2230;--muted:#5c667a;--line:#e1e6ee;--accent:#2f6df0;
 --keep:#1f9d55;--keepbg:#e6f5ec;--unsure:#c98a1a;--unsurebg:#fbf3e0;--drop:#d1443f;--dropbg:#fbe7e6;--mono:ui-monospace,Menlo,Consolas,monospace}
@media(prefers-color-scheme:dark){:root{--bg:#0e131a;--panel:#161d27;--ink:#e7edf5;--muted:#909cb0;--line:#25303f;--keepbg:#12291c;--unsurebg:#2c2412;--dropbg:#2c1616}}
:root[data-theme=dark]{--bg:#0e131a;--panel:#161d27;--ink:#e7edf5;--muted:#909cb0;--line:#25303f;--keepbg:#12291c;--unsurebg:#2c2412;--dropbg:#2c1616}
:root[data-theme=light]{--bg:#f5f7fa;--panel:#fff;--ink:#1a2230;--muted:#5c667a;--line:#e1e6ee;--keepbg:#e6f5ec;--unsurebg:#fbf3e0;--dropbg:#fbe7e6}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;z-index:10;background:var(--panel);border-bottom:1px solid var(--line);padding:12px 18px;box-shadow:0 1px 6px #0001}
h1{font-size:17px;margin:0 0 8px}
.stats{font-size:12px;color:var(--muted);margin:0 0 8px;line-height:1.7}.stats b{color:var(--ink)}.stats code{font-family:var(--mono);background:#0000000d;padding:1px 5px;border-radius:4px}
@media(prefers-color-scheme:dark){.stats code{background:#ffffff14}}
.note{font-size:12px;color:var(--muted);margin:0 0 10px;padding:7px 10px;border:1px dashed var(--line);border-radius:7px}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
select,input,button{font:inherit;padding:6px 10px;border:1px solid var(--line);border-radius:7px;background:var(--panel);color:var(--ink)}
input#q{min-width:230px}button{cursor:pointer}button:hover{border-color:var(--accent)}
.count{font-family:var(--mono);font-size:12.5px;padding:4px 9px;border-radius:999px;border:1px solid var(--line)}
.count.k{color:var(--keep)}.count.u{color:var(--unsure)}.count.d{color:var(--drop)}.count.n{color:var(--muted)}
#export{margin-left:auto;background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
main{padding:0 18px 60px}table{border-collapse:collapse;width:100%}
th,td{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{position:sticky;top:0;background:var(--panel);font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
td.num,td.dur,td.ni{font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap;color:var(--muted)}
td.task{min-width:280px}td.q{min-width:200px;color:var(--muted);font-size:13px}td.dom{white-space:nowrap}
.dup{display:inline-block;font-family:var(--mono);font-size:10.5px;color:var(--unsure);border:1px solid var(--unsure);border-radius:4px;padding:0 4px;margin-left:5px}
a.play{color:var(--accent);text-decoration:none;font-weight:600}a.play.off{color:var(--muted);opacity:.55;pointer-events:none;font-weight:400}
tr.keep{background:var(--keepbg)}tr.unsure{background:var(--unsurebg)}tr.drop{background:var(--dropbg)}
.sb{display:flex;gap:3px}.sb button{padding:3px 7px;font-size:11.5px;border-radius:5px;line-height:1.3}
.sb button.k.on{background:var(--keep);color:#fff;border-color:var(--keep)}.sb button.u.on{background:var(--unsure);color:#fff;border-color:var(--unsure)}.sb button.d.on{background:var(--drop);color:#fff;border-color:var(--drop)}
.hint{color:var(--muted);font-size:12px}
</style></head><body>
<header>
<h1>EgoProactive interrupt-segmentation screening — <span id=shown>700</span>/700 shown</h1>
<div class=stats id=summary></div>
<div class=note>▶ <b>play</b> opens the mp4 in a new tab — needs the videos downloaded into <code>./videos</code> and this page served from the repo root (<code>python3 vlm/serve_review.py --dir . --port 8768</code> → open <code>/screening/screening.html</code>; see README.md). No videos? You can still screen by the task/query text; marks &amp; export work offline.</div>
<div class=controls>
  <select id=dom><option value="">All domains</option>__DOMOPTS__</select>
  <input id=q placeholder="search task / query / id…">
  <button id=sortdur>Sort: duration ▲</button>
  <button id=sorttask>Group by task</button>
  <button id=reset>Reset order</button>
  <span class=count k>keep <b id=ck>0</b></span>
  <span class=count u>unsure <b id=cu>0</b></span>
  <span class=count d>drop <b id=cd>0</b></span>
  <span class=count n>unmarked <b id=cn>700</b></span>
  <button id=export>⬇ Export decisions</button>
</div></header>
<main><table><thead><tr>
<th>#</th><th>play</th><th>video_path</th><th>domain</th><th>dur(s)</th><th title="existing video_intervals count">#iv</th><th>task (full)</th><th>query</th><th>decision</th>
</tr></thead><tbody id=tb></tbody></table><p class=hint id=empty style=display:none>No rows match the current filter.</p></main>
<script>
const DATA=__DATA__, STATS=__STATS__, LS="egoproactive_screening_v1";
let store=JSON.parse(localStorage.getItem(LS)||"{}");
const $=s=>document.querySelector(s);
$("#summary").innerHTML=`<b>${STATS.n}</b> videos &nbsp;|&nbsp; duration min/median/max = `+
 `<code>${STATS.dur_min}</code>/<code>${STATS.dur_med}</code>/<code>${STATS.dur_max}</code>s · `+
 Object.entries(STATS.dur_buckets).map(([k,v])=>`${k}: <b>${v}</b>`).join(" · ")+
 `<br><b>${STATS.uniq_tasks}</b> unique tasks · <b>${STATS.dup_tasks}</b> tasks have &gt;1 video `+
 `(<b>${STATS.vids_in_dup_tasks}</b> videos share a task; max <b>${STATS.max_vids_per_task}</b>/task) — "Group by task" to batch-decide.`+
 `<br>Domains: `+Object.entries(STATS.domains).map(([k,v])=>`${k} <b>${v}</b>`).join(" · ");
let order=DATA.map((_,i)=>i), durAsc=true;
function counts(){let k=0,u=0,d=0;for(const x of DATA){const s=store[x.vp];if(s=="keep")k++;else if(s=="unsure")u++;else if(s=="drop")d++;}
 $("#ck").textContent=k;$("#cu").textContent=u;$("#cd").textContent=d;$("#cn").textContent=DATA.length-k-u-d;}
function esc(s){const e=document.createElement("span");e.textContent=s;return e.innerHTML;}
function rowHTML(d){const s=store[d.vp]||"";
 const play=d.dl?`<a class=play href="../videos/${d.vp}" target=_blank rel=noopener>▶ play</a>`:`<a class="play off" title="not downloaded">▶ n/a<br><span style=font-size:10px>未下载</span></a>`;
 const dup=d.dup>1?`<span class=dup title="${d.dup} videos share this exact task">×${d.dup}</span>`:"";
 return `<tr class="${s}" data-vp="${esc(d.vp)}"><td class=num>${d.i}</td><td>${play}</td><td class=num>${esc(d.vp)}</td>`+
 `<td class=dom>${esc(d.dom)}</td><td class=dur>${d.dur}</td><td class=ni>${d.ni}</td><td class=task>${esc(d.task)}${dup}</td><td class=q>${esc(d.q)}</td>`+
 `<td><div class=sb><button class="k${s=='keep'?' on':''}" data-a=keep>keep</button><button class="u${s=='unsure'?' on':''}" data-a=unsure>unsure</button><button class="d${s=='drop'?' on':''}" data-a=drop>drop</button></div></td></tr>`;}
function render(){const domf=$("#dom").value,qf=$("#q").value.trim().toLowerCase();
 let vis=order.filter(i=>{const d=DATA[i];if(domf&&d.dom!=domf)return false;
   if(qf&&!(d.task.toLowerCase().includes(qf)||d.q.toLowerCase().includes(qf)||d.vp.toLowerCase().includes(qf)||String(d.i)==qf))return false;return true;});
 $("#tb").innerHTML=vis.map(i=>rowHTML(DATA[i])).join("");$("#shown").textContent=vis.length;$("#empty").style.display=vis.length?"none":"block";}
$("#tb").addEventListener("click",e=>{const b=e.target.closest("button[data-a]");if(!b)return;
 const tr=b.closest("tr"),vp=tr.dataset.vp,a=b.dataset.a;if(store[vp]==a)delete store[vp];else store[vp]=a;
 localStorage.setItem(LS,JSON.stringify(store));tr.className=store[vp]||"";
 tr.querySelectorAll(".sb button").forEach(x=>x.classList.toggle("on",x.dataset.a==store[vp]));counts();});
$("#dom").onchange=render;let t;$("#q").oninput=()=>{clearTimeout(t);t=setTimeout(render,120);};
$("#sortdur").onclick=()=>{durAsc=!durAsc;order=DATA.map((_,i)=>i).sort((a,b)=>durAsc?DATA[a].dur-DATA[b].dur:DATA[b].dur-DATA[a].dur);$("#sortdur").textContent="Sort: duration "+(durAsc?"▲":"▼");render();};
$("#sorttask").onclick=()=>{order=DATA.map((_,i)=>i).sort((a,b)=>DATA[a].task.localeCompare(DATA[b].task)||DATA[a].dur-DATA[b].dur);render();};
$("#reset").onclick=()=>{order=DATA.map((_,i)=>i);durAsc=true;$("#sortdur").textContent="Sort: duration ▲";render();};
$("#export").onclick=()=>{const out=DATA.map(d=>({video_path:d.vp,decision:store[d.vp]||"unmarked"}));
 const blob=new Blob([JSON.stringify(out,null,1)],{type:"application/json"});const a=document.createElement("a");
 a.href=URL.createObjectURL(blob);a.download="screening_decisions.json";a.click();URL.revokeObjectURL(a.href);};
counts();render();
</script></body></html>'''
html = TEMPLATE.replace("__DATA__", DATA).replace("__STATS__", STATS).replace("__DOMOPTS__", domopts)
open(os.path.join(ROOT, "screening.html"), "w").write(html)
print("wrote screening.html", round(len(html)/1024), "KB |", stats["n"], "rows |", stats["downloaded"], "downloaded on this machine")
