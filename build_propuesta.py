# -*- coding: utf-8 -*-
"""Genera propuesta/index.html — página de precios del agente de AsoBares.

Sistema de diseño: Propuestas comerciales (skill diseno-propuestas-comerciales)
  · Superficie Compare: 3 columnas alineadas, una destacada como RECOMENDADA
  · IBM Plex Sans + IBM Plex Mono; mono solo para labels, números y kickers
  · Teal #0f766e como único acento; fondos #fff / #f6f8f8 / #eef7f6
  · Radios 14px cards, 9px botones

Fondo del título: Dither Canvas de ObsidianUI (dither_js.py) — réplica fiel del
efecto original: superficie blanca opaca, rejilla fina de 110 columnas, matriz
de Bayer y simulación de fluido. La señal es procedural porque el proyecto no
cuenta con el video que usa el original.
"""
import html as H
import os
from data_precios import PRECIO_BASE, PRECIO_IVA, PRECIO_FINAL, MENSAJES_INCLUIDOS
from simulacion_tokens import filas_perfiles, filas_plan, sensibilidad
from simulador_js import SIM_JS
from dither_js import dither_js, TEAL

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "propuesta")
os.makedirs(OUT, exist_ok=True)


def esc(s):
    return H.escape(str(s), quote=False)


# ---------- Filas de tablas ----------
perfil_rows = "\n".join(
    f"<tr><td class='rowhead'>{esc(e)}</td><td class='num'>{n}</td>"
    f"<td class='num'>{esc(o)}</td><td class='num'>{esc(tk)}</td>"
    f"<td class='num'><span class='strong'>${esc(cc)}</span></td>"
    f"<td class='num muted-sm'>${esc(sc)}</td></tr>"
    for e, n, o, tk, cc, sc, _ in filas_perfiles())

plan_rows = "\n".join(
    f"<tr><td class='rowhead'>{esc(e)}</td><td class='num'>{esc(cv)}</td>"
    f"<td class='num'><span class='strong'>${esc(cc)}</span></td>"
    f"<td class='num muted-sm'>${esc(sc)}</td>"
    f"<td class='num'>{esc(pc)}%</td></tr>"
    for e, cv, cc, sc, pc in filas_plan())

sens_cols = "\n".join(
    f"<tr><td class='rowhead'>{esc(e)}</td><td class='num'>${esc(v)}</td>"
    f"<td class='num'>{esc(r)}</td><td class='muted-sm'>{esc(no)}</td></tr>"
    for e, v, r, no in sensibilidad())

# Componentes medidos del prompt (de simulacion_tokens.py)
from simulacion_tokens import COMPONENTES_PROMPT, FIJO, CACHEABLE
comp_rows = "\n".join(
    f"<tr><td class='rowhead'>{esc(c)}</td><td class='muted-sm'>{esc(d)}</td>"
    f"<td class='num'><span class='strong'>{esc(t)}</span></td>"
    f"<td class='muted-sm'>{esc(n)}</td></tr>"
    for c, d, t, n in COMPONENTES_PROMPT)

# Medición de la conversación real (contar_tokens_conversacion.py)
CONV_MEDIDA = [
    ("Mensajes en el chat", "16", "8 del cliente, 8 del agente"),
    ("Tokens de texto en pantalla", "693", "Lo que se ve en el chat"),
    ("Llamadas al LLM", "8", "Una por mensaje del cliente"),
    ("Entrada facturada", "25.394", "36,6× el texto: el historial se reenvía"),
    ("Salida", "506", "82 tokens por respuesta"),
    ("Costo de la conversación", "$3,26", "Con caché de prompt, off-peak"),
]
medida_rows = "\n".join(
    f"<tr><td class='rowhead'>{esc(c)}</td><td class='num'><span class='strong'>{esc(v)}</span></td>"
    f"<td class='muted-sm'>{esc(n)}</td></tr>"
    for c, v, n in CONV_MEDIDA)

# Slices de InterServer
SLICES = [
    ("1 slice", "1", "2", "40", "3,00", "12.000", "50", "El plan Esencial corre aquí", "rec"),
    ("2 slices", "2", "4", "80", "6,00", "24.000", "100", "Crecimiento cómodo", ""),
    ("4 slices", "2", "8", "160", "12,00", "48.000", "100", "El análisis original pedía esta talla", ""),
    ("8 slices", "4", "16", "320", "24,00", "96.000", "200", "Soporte gestionado incluido", ""),
    ("16 slices", "8", "32", "640", "48,00", "192.000", "400", "Varios capítulos regionales", ""),
]
slices_rows = "\n".join(
    f"<tr><td class='rowhead'>{esc(n)}</td><td class='num'>{esc(co)}</td>"
    f"<td class='num'>{esc(ra)} GB</td><td class='num'>{esc(di)} GB</td>"
    f"<td class='num'>US$ {esc(u)}</td>"
    f"<td class='num{' col-rec' if rc else ''}'>${esc(cp)}</td>"
    f"<td class='num{' col-rec' if rc else ''}'><span class='strong'>{esc(neg)}</span></td>"
    f"<td class='muted-sm'>{esc(no)}</td></tr>"
    for n, co, ra, di, u, cp, neg, no, rc in SLICES)

CSS = r"""
:root{
  --bg:#ffffff;--bg-soft:#f6f8f8;--bg-accent:#eef7f6;
  --ink:#10201e;--ink-2:#33423f;--muted:#64716e;
  --line:#e3e8e7;--line-strong:#cdd6d4;
  --accent:#0f766e;--accent-strong:#0b5e58;--accent-soft:#e6f4f2;--accent-ring:rgba(15,118,110,.25);
  --ok:#1a7f4e;--warn:#b45309;--danger:#b42318;
  --radius:14px;--radius-sm:9px;
  --shadow-card:0 1px 2px rgba(16,32,30,.05);
  --shadow-rec:0 18px 44px -18px rgba(15,118,110,.35), 0 2px 6px rgba(16,32,30,.06);
  --mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  --sans:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:84px}
body{font-family:var(--sans);color:var(--ink);background:var(--bg);line-height:1.55;font-size:16px;-webkit-font-smoothing:antialiased}
::selection{background:var(--accent-soft)}
a{color:var(--accent-strong);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1160px;margin:0 auto;padding:0 24px}
.mono{font-family:var(--mono)}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums}

/* ---------- Topbar ---------- */
.topbar{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.9);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.topbar-inner{display:flex;align-items:center;justify-content:space-between;gap:16px;height:60px}
.brand{display:flex;align-items:center;gap:10px;font-weight:600;font-size:14px;letter-spacing:.2px}
.brand svg{flex:none}
.brand .sub{color:var(--muted);font-weight:500}
.topbar nav{display:flex;gap:22px;font-size:13.5px;font-weight:500}
.topbar nav a{color:var(--ink-2)}
.topbar nav .pill{font-family:var(--mono);font-size:11.5px;background:var(--accent-soft);color:var(--accent-strong);padding:6px 10px;border-radius:99px;margin-left:8px}
.btn-print{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:12.5px;font-weight:600;color:#fff;background:var(--accent);border:1px solid var(--accent);padding:9px 14px;border-radius:var(--radius-sm);cursor:pointer;transition:background .15s}
.btn-print:hover{background:var(--accent-strong)}
.btn-print svg{flex:none}

/* ---------- Hero con Dither Canvas de fondo ---------- */
.hero{position:relative;padding:76px 0 54px;background:linear-gradient(180deg,var(--bg-soft) 0%,var(--bg) 100%);border-bottom:1px solid var(--line);overflow:hidden}
.hero-bg{position:absolute;inset:0;z-index:0;pointer-events:none}
.hero-bg::before{content:"";position:absolute;inset:-40px;
  background:
    radial-gradient(42% 90% at 6% 58%, rgba(230,244,242,.95), transparent 64%),
    radial-gradient(40% 85% at 30% 26%, rgba(15,118,110,.20), transparent 64%),
    radial-gradient(46% 92% at 56% 48%, rgba(13,148,136,.22), transparent 68%),
    radial-gradient(50% 100% at 82% 34%, rgba(15,118,110,.30), transparent 66%),
    radial-gradient(36% 82% at 100% 60%, rgba(26,127,78,.18), transparent 62%);
  filter:blur(8px)}
.dither-fallback{position:absolute;inset:0;z-index:1;pointer-events:none;
  background-image:linear-gradient(135deg,transparent 12%,#0f766e 35%,#0d9488 55%,#0b5e58 72%,transparent 90%);
  -webkit-mask-image:radial-gradient(circle,#000 1px,transparent 1.3px);
  mask-image:radial-gradient(circle,#000 1px,transparent 1.3px);
  -webkit-mask-size:7px 7px;mask-size:7px 7px;opacity:.4}
#dither{position:absolute;inset:0;z-index:2;width:100%;height:100%;display:block;
  opacity:0;transition:opacity .6s ease;pointer-events:auto;cursor:crosshair}
/* Velo direccional: opaco donde va el texto (izquierda) y abierto hacia la
   derecha, para que el dither se vea nítido en lugar de lavado. */
.hero::after{content:"";position:absolute;inset:0;z-index:3;pointer-events:none;
  background:
    linear-gradient(90deg, rgba(255,255,255,.76) 0%, rgba(255,255,255,.56) 38%,
                    rgba(255,255,255,.30) 62%, rgba(255,255,255,.10) 84%,
                    rgba(255,255,255,0) 100%),
    linear-gradient(180deg, rgba(255,255,255,.48) 0%, rgba(255,255,255,0) 26%,
                    rgba(255,255,255,0) 58%, var(--bg) 100%)}
.hero .wrap{position:relative;z-index:4}
/* Refuerzo local bajo el bloque de texto, no en toda la banda. */
.hero .wrap::before{content:"";position:absolute;inset:-22px -34px -18px -34px;z-index:-1;
  border-radius:20px;
  background:radial-gradient(72% 88% at 30% 44%, rgba(255,255,255,.90), rgba(255,255,255,.58) 58%, rgba(255,255,255,.12) 100%)}
.mesh-hint{position:absolute;right:24px;top:74px;z-index:5;font-family:var(--mono);font-size:10px;
  letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);background:rgba(255,255,255,.8);
  backdrop-filter:blur(6px);border:1px solid var(--line-strong);border-radius:99px;padding:5px 11px;
  pointer-events:none}

.eyebrow{font-family:var(--mono);font-size:12px;font-weight:600;letter-spacing:1.6px;text-transform:uppercase;color:var(--accent);display:flex;align-items:center;gap:10px}
.eyebrow::before{content:"";width:26px;height:1.5px;background:var(--accent)}
.hero h1{font-size:clamp(30px,4.4vw,50px);line-height:1.08;letter-spacing:-1.2px;font-weight:700;margin:18px 0 18px;max-width:860px}
.hero h1 em{font-style:normal;color:var(--accent)}
.hero p.lead{font-size:17.5px;color:var(--ink-2);max-width:780px}
.drivers{display:flex;flex-wrap:wrap;gap:10px;margin-top:26px}
.drivers span{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:12.5px;color:var(--ink-2);border:1px solid var(--line-strong);background:rgba(255,255,255,.86);backdrop-filter:blur(4px);padding:8px 13px;border-radius:99px}
.drivers svg{flex:none}
.hero-cta{margin-top:30px;display:flex;gap:12px;flex-wrap:wrap}
.cta{display:inline-flex;align-items:center;gap:8px;font-weight:600;font-size:14.5px;padding:12px 20px;border-radius:var(--radius-sm);transition:background .15s}
.cta.primary{background:var(--accent);color:#fff}
.cta.primary:hover{background:var(--accent-strong);text-decoration:none}
.cta.ghost{border:1px solid var(--line-strong);color:var(--ink-2);background:rgba(255,255,255,.86)}
.cta.ghost:hover{background:var(--bg-soft);text-decoration:none}

/* ---------- Section scaffolding ---------- */
section{padding:64px 0}
.sec-head{margin-bottom:34px}
.sec-kicker{font-family:var(--mono);font-size:11.5px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--accent)}
.sec-title{font-size:clamp(24px,3vw,34px);letter-spacing:-.6px;font-weight:700;margin-top:8px}
.sec-sub{color:var(--muted);margin-top:10px;max-width:760px;font-size:15.5px}

/* ---------- Compare cards ---------- */
.compare{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;align-items:stretch}
.card{position:relative;background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:26px 24px 24px;display:flex;flex-direction:column;gap:18px;box-shadow:var(--shadow-card)}
.card.muted{background:var(--bg-soft)}
.card.rec{border:1.5px solid var(--accent);box-shadow:var(--shadow-rec);background:var(--bg-accent)}
.badge-rec{position:absolute;top:-13px;left:24px;display:inline-flex;align-items:center;gap:6px;font-family:var(--mono);font-size:11px;font-weight:600;letter-spacing:.8px;text-transform:uppercase;color:#fff;background:var(--accent);padding:5px 12px;border-radius:99px;box-shadow:0 4px 12px rgba(15,118,110,.35)}
.opt-no{font-family:var(--mono);font-size:11.5px;font-weight:600;letter-spacing:1.4px;color:var(--muted)}
.card.rec .opt-no{color:var(--accent-strong)}
.card h3{font-size:20px;letter-spacing:-.3px;font-weight:700;margin-top:5px;line-height:1.2}
.card .concept{font-size:14px;color:var(--ink-2)}
.spec{display:flex;flex-direction:column;gap:8px;border-top:1px solid var(--line);padding-top:16px}
.spec .k{font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:1.1px;text-transform:uppercase;color:var(--muted)}
.spec .v{font-size:13.5px;color:var(--ink);line-height:1.5}
.spec .v strong{font-weight:600}
.risk{font-size:13.5px;color:var(--ink-2);border-top:1px solid var(--line);padding-top:14px;display:flex;gap:9px;align-items:flex-start}
.risk svg{flex:none;margin-top:3px}
.risk.warn svg circle.r{stroke:var(--warn)}
.risk.ok svg circle.r{stroke:var(--ok)}
.price{border-top:1px solid var(--line);padding-top:18px;margin-top:auto}
.price-label{font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:1.1px;text-transform:uppercase;color:var(--muted)}
.price-amount{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:32px;font-weight:600;letter-spacing:-1.3px;line-height:1.05;margin-top:7px;color:var(--ink)}
.card.rec .price-amount{color:var(--accent-strong)}
.card.muted .price-amount{color:var(--ink-2)}
.price-amount.is-text{font-family:var(--sans);font-size:25px;font-weight:700;letter-spacing:-.6px}
.price-cur{font-family:var(--sans);font-size:11.5px;font-weight:500;letter-spacing:0;color:var(--muted);margin-left:7px;vertical-align:2px}
.price-note{font-size:12.5px;color:var(--muted);margin-top:5px;line-height:1.45}
.price-note .num{color:var(--ink-2);font-weight:600}
.price-metrics{display:grid;grid-template-columns:1fr 1fr;gap:9px 12px;margin-top:15px;padding-top:13px;border-top:1px dashed var(--line-strong)}
.price-metrics>div{display:flex;flex-direction:column;gap:2px;min-width:0}
.price-metrics .k{font-family:var(--mono);font-size:9.5px;font-weight:600;letter-spacing:.85px;text-transform:uppercase;color:var(--muted)}
.price-metrics .v{font-size:13.5px;font-weight:600;color:var(--ink);letter-spacing:-.2px}
.card.rec .price-metrics .v{color:var(--accent-strong)}
.card.muted .price-metrics .v{color:var(--ink-2)}
.card-link{display:inline-flex;align-items:center;gap:7px;margin-top:16px;font-size:13.5px;font-weight:600}
.card-link svg{flex:none;transition:transform .18s ease}
.card-link:hover{text-decoration:none}
.card-link:hover svg{transform:translateX(3px)}
.tag{display:inline-block;font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:.6px;padding:3px 8px;border-radius:6px;background:var(--bg-soft);color:var(--ink-2);border:1px solid var(--line-strong)}
.card.rec .tag{background:var(--accent-soft);border-color:transparent;color:var(--accent-strong)}

/* ---------- Topology strip ---------- */
.topology{display:grid;grid-template-columns:1fr 44px 1fr 44px 1fr;align-items:stretch;gap:0;margin-top:36px;border:1px solid var(--line);border-radius:var(--radius);background:#fff;overflow:hidden}
.topo-node{padding:22px 18px;display:flex;flex-direction:column;gap:7px}
.topo-node .role{font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:1.1px;text-transform:uppercase}
.topo-node .hw{font-size:14px;font-weight:600;line-height:1.3}
.topo-node .job{font-size:12.5px;color:var(--muted)}
.topo-node.a{background:var(--ink);color:#fff}
.topo-node.a .role{color:#7dd3c8}
.topo-node.a .job{color:#b9c6c3}
.topo-node.b{background:var(--bg-soft)}
.topo-node.c{background:var(--bg-accent)}
.topo-arrow{display:flex;align-items:center;justify-content:center;color:var(--accent)}

/* ---------- Detail blocks ---------- */
.detail{display:grid;grid-template-columns:52px 1fr;gap:22px;padding:30px 0;border-top:1px solid var(--line)}
.detail .dnum{font-family:var(--mono);font-size:12px;font-weight:600;color:var(--muted);line-height:1.6;padding-top:2px}
.detail.rec .dnum{color:var(--accent-strong)}
.detail h3{font-size:20px;letter-spacing:-.3px;font-weight:700}
.detail .dsub{font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:3px}
.detail p{margin-top:12px;font-size:15px;color:var(--ink-2);max-width:860px}
.detail ul{margin:12px 0 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px;max-width:860px}
.detail li{font-size:14.5px;color:var(--ink-2);padding-left:22px;position:relative}
.detail li::before{content:"";position:absolute;left:4px;top:9px;width:6px;height:6px;border-radius:2px;background:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;max-width:860px}

/* ---------- Table ---------- */
.table-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:#fff}
table.cmp{width:100%;border-collapse:collapse;min-width:880px}
table.cmp th,table.cmp td{padding:13px 16px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:13.5px}
table.cmp thead th{font-family:var(--mono);font-size:11px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--muted);background:var(--bg-soft);position:sticky;top:60px;z-index:2}
table.cmp thead th.col-rec{background:var(--accent-soft);color:var(--accent-strong)}
table.cmp td.rowhead{font-family:var(--mono);font-size:11.5px;font-weight:600;letter-spacing:.5px;color:var(--muted);background:var(--bg-soft);width:170px}
table.cmp tbody td.col-rec{background:var(--bg-accent)}
table.cmp tbody tr:last-child td{border-bottom:none}
table.cmp td .strong{font-weight:600}
table.cmp td .muted-sm{color:var(--muted);font-size:12.5px}
.rec-note{display:flex;gap:12px;align-items:flex-start;margin-top:22px;padding:16px 18px;background:var(--accent-soft);border:1px solid var(--accent-ring);border-radius:var(--radius-sm);font-size:14px;color:var(--ink-2)}
.rec-note svg{flex:none;margin-top:2px}
.note-warn{background:#fdf6ec;border-color:rgba(180,83,9,.28)}
.note-warn svg{stroke:var(--warn)}

/* ---------- Simulador ---------- */
.sim{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.sim-panel{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:24px;box-shadow:var(--shadow-card)}
.sim-result{background:var(--ink);color:#fff;border-color:transparent;box-shadow:var(--shadow-rec)}
.sim-label{display:block;font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:1.1px;text-transform:uppercase;color:var(--muted);margin:0 0 8px}
.sim-result .sim-label{color:rgba(255,255,255,.72)}
.sim-readout{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:30px;font-weight:600;letter-spacing:-.8px;line-height:1.1;margin-bottom:10px}
.sim-readout-sm{font-size:22px}
.sim-unit{font-family:var(--sans);font-size:13px;font-weight:500;color:var(--muted);letter-spacing:0}
.sim-scale{display:flex;justify-content:space-between;font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:4px}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:22px;background:transparent;cursor:pointer;margin:0}
input[type=range]::-webkit-slider-runnable-track{height:3px;background:var(--line-strong);border-radius:99px}
input[type=range]::-moz-range-track{height:3px;background:var(--line-strong);border-radius:99px}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:18px;height:18px;border-radius:99px;background:var(--accent);border:3px solid #fff;margin-top:-8px;box-shadow:var(--shadow-card)}
input[type=range]:focus-visible::-webkit-slider-thumb{outline:2px solid var(--accent-strong);outline-offset:2px}
input[type=range]::-moz-range-thumb{width:18px;height:18px;border-radius:99px;background:var(--accent);border:3px solid #fff}
.sim-presets{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:18px 0 20px}
.sim-preset{font-family:var(--sans);font-weight:500;font-size:12.5px;text-align:left;line-height:1.3;padding:10px 12px;border:1px solid var(--line-strong);border-radius:var(--radius-sm);background:var(--bg-soft);color:var(--ink-2);cursor:pointer;transition:border-color .15s,background .15s,color .15s}
.sim-preset span{display:block;font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:2px;font-variant-numeric:tabular-nums}
.sim-preset:hover{border-color:var(--accent);color:var(--accent-strong)}
.sim-preset.on{background:var(--accent-soft);border-color:var(--accent);color:var(--accent-strong);font-weight:600}
.sim-toggle{display:flex;margin-bottom:8px;border:1px solid var(--line-strong);border-radius:99px;overflow:hidden;width:fit-content}
.sim-toggle button{font-family:var(--mono);font-size:12px;font-weight:600;padding:7px 16px;border:none;background:#fff;color:var(--ink-2);cursor:pointer;transition:background .15s,color .15s}
.sim-toggle button:hover{background:var(--bg-soft);color:var(--accent-strong)}
.sim-toggle button.on{background:var(--accent);color:#fff}
select{width:100%;font-family:var(--sans);font-weight:500;font-size:13.5px;padding:9px 12px;border:1px solid var(--line-strong);border-radius:var(--radius-sm);background:#fff;color:var(--ink);margin-bottom:20px;cursor:pointer}
select:focus{border-color:var(--accent);outline:none;box-shadow:0 0 0 3px var(--accent-ring)}
.sim-hint{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin-top:6px;font-variant-numeric:tabular-nums}
.sim-hint.over{color:var(--warn);font-weight:600}
.sim-res-head{border-bottom:1px solid rgba(255,255,255,.16);padding-bottom:18px;margin-bottom:6px}
.sim-res-tag{font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:1.1px;text-transform:uppercase;opacity:.72}
.sim-big{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:40px;font-weight:600;letter-spacing:-1.2px;line-height:1.05;margin:8px 0 4px}
.sim-per{font-family:var(--sans);font-size:13px;font-weight:500;opacity:.72;letter-spacing:0;margin-left:6px}
.sim-big-sub{font-family:var(--mono);font-size:12px;opacity:.74}
.sim-rows{margin:14px 0 0}
.sim-row{display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.1);font-size:13.5px}
.sim-row:last-child{border-bottom:none}
.sim-row dt{opacity:.86}
.sim-row dd{font-family:var(--mono);font-variant-numeric:tabular-nums;font-weight:600}
.sim-int{font-family:var(--mono);font-size:9px;letter-spacing:.8px;text-transform:uppercase;opacity:.55;border:1px solid rgba(255,255,255,.3);border-radius:99px;padding:1px 6px;margin-left:4px}
.sim-sup{font-family:var(--mono);font-size:9.5px;letter-spacing:.8px;text-transform:uppercase;opacity:.6;margin-left:4px}
.sim-row-hi dt,.sim-row-hi dd{color:#7dd3c8}
.sim-sep{border-top:1px solid rgba(255,255,255,.22);margin-top:6px;padding-top:13px}
.sim-row-margen dt,.sim-row-margen dd{padding-top:12px;border-top:1px solid rgba(255,255,255,.22);margin-top:4px}
.sim-pct{font-size:11.5px;opacity:.75;margin-left:6px}
.sim-bar{margin-top:20px}
.sim-bar-lbl{font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:1.1px;text-transform:uppercase;opacity:.72;display:block;margin-bottom:8px}
.sim-bar-track{height:7px;border-radius:99px;overflow:hidden;background:rgba(255,255,255,.18)}
.sim-bar-fill{display:block;height:100%;background:linear-gradient(90deg,#7dd3c8,var(--accent));border-radius:99px;transition:width .35s ease}
.sim-bar-legend{display:flex;gap:16px;margin-top:10px;font-family:var(--mono);font-size:11px;opacity:.84;flex-wrap:wrap}
.sim-bar-legend span{display:flex;align-items:center;gap:5px}
.sim-bar-legend b{font-weight:600}
.sw{width:8px;height:8px;border-radius:2px;display:inline-block;flex:none}
.sw-margen{background:#7dd3c8}
.sw-ia{background:#f0a05a}
.sw-infra{background:#9fb3b0}

/* ---------- Footer ---------- */
footer{border-top:1px solid var(--line);background:var(--bg-soft);padding:34px 0;font-size:13px;color:var(--muted)}
.foot{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
.foot .mono{font-size:12px}

/* ---------- Reveal ---------- */
.reveal{opacity:0;transform:translateY(14px);transition:opacity .5s ease,transform .5s ease}
.reveal.in{opacity:1;transform:none}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .reveal{opacity:1;transform:none;transition:none}
}

/* ---------- Responsive ---------- */
@media (max-width:980px){
  .compare{grid-template-columns:1fr}
  .card.rec{order:-1}
  .topology{grid-template-columns:1fr;grid-auto-rows:auto}
  .topo-arrow{transform:rotate(90deg);padding:6px 0}
  .topbar nav{display:none}
  .sim{grid-template-columns:1fr}
  .sim-big{font-size:34px}
}
@media (max-width:640px){
  .hero{padding:52px 0 34px}
  section{padding:46px 0}
  .detail{grid-template-columns:1fr;gap:10px}
  .brand .sub{display:none}
  .mesh-hint{display:none}
  .sim-presets{grid-template-columns:1fr}
}

/* ---------- Print ---------- */
@media print{
  @page{margin:14mm 12mm}
  body{font-size:11.5px;background:#fff}
  .topbar{position:static;backdrop-filter:none;border-bottom:1px solid var(--line)}
  .btn-print,.hero-cta,.topbar nav,.hero-bg,.mesh-hint{display:none !important}
  .hero{padding:26px 0 14px;background:none;border-bottom:1px solid var(--line)}
  .hero::after{display:none}
  .reveal{opacity:1;transform:none}
  .compare{grid-template-columns:1fr 1fr 1fr;gap:10px}
  .card{padding:14px;break-inside:avoid;box-shadow:none}
  .card.rec{order:0}
  section{padding:18px 0}
  .detail{padding:14px 0;break-inside:avoid}
  .topology,.sim{break-inside:avoid}
  .table-scroll{overflow:visible}
  table.cmp{min-width:0}
  table.cmp thead th{position:static;background:var(--bg-soft)}
  .topbar-inner{height:44px}
  footer{display:none}
  *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
"""

html_doc = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agente de AsoBares · Propuesta de precios</title>
<meta name="description" content="Precios del agente de WhatsApp con IA para los afiliados de AsoBares: tres modalidades desde $80.000 + IVA, costo real de IA medido con DeepSeek V4.1 Flash, capacidad por slices de InterServer y simulador de consumo.">
<meta property="og:title" content="Agente de AsoBares · Propuesta de precios">
<meta property="og:description" content="Comparación de tres modalidades de servicio, con el costo real de operar el agente medido sobre el código y una conversación real.">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cpath d='M16 2 28 9v14L16 30 4 23V9z' fill='%230f766e'/%3E%3Cpath d='M11 16.5l3.5 3.5L21 13' stroke='%23fff' stroke-width='2.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<header class="topbar">
  <div class="wrap topbar-inner">
    <div class="brand">
      <svg width="22" height="22" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 2 28 9v14L16 30 4 23V9z" fill="#0f766e"/><path d="M11 16.5l3.5 3.5L21 13" stroke="#fff" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <span>Agente de WhatsApp <span class="sub">· AsoBares</span></span>
    </div>
    <nav aria-label="Secciones">
      <a href="#opciones">Modalidades</a>
      <a href="#capacidad">Capacidad</a>
      <a href="#simulador">Simulador</a>
      <a href="#comparativa">Comparativa <span class="pill">3 opciones</span></a>
    </nav>
    <button class="btn-print" onclick="window.print()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
      Exportar PDF
    </button>
  </div>
</header>

<main>
  <section class="hero">
    <div class="hero-bg" aria-hidden="true">
      <div class="dither-fallback"></div>
      <canvas id="dither"></canvas>
    </div>
    <span class="mesh-hint" aria-hidden="true">Mueve el cursor</span>
    <div class="wrap">
      <div class="eyebrow">Propuesta comercial · Afiliados AsoBares</div>
      <h1>Un agente de WhatsApp que atiende tu bar <em>24/7</em></h1>
      <p class="lead">Un solo plan de $80.000 + IVA con 1.000 mensajes incluidos, y bloques de 1.000 mensajes a $30.000 para cuando el bar necesite más. El agente responde el menú, los horarios, toma reservas y registra pedidos. El costo real de operarlo está medido sobre el código del agente y sobre una conversación de WhatsApp real, no estimado.</p>
      <div class="drivers" aria-label="Principios del servicio">
        <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0f766e" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>Servidor compartido</span>
        <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0f766e" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>Costo medido, no estimado</span>
        <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0f766e" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>Ley 1581 de 2012</span>
      </div>
      <div class="hero-cta">
        <a class="cta primary" href="#opciones">Ver precios
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
        <a class="cta ghost" href="#simulador">Calcular mi consumo</a>
      </div>
    </div>
  </section>

  <section id="opciones">
    <div class="wrap">
      <div class="sec-head reveal">
        <div class="sec-kicker">Modalidades</div>
        <h2 class="sec-title">Un plan, bloques de mensajes y una medida a la carta</h2>
        <p class="sec-sub">Hay un solo plan que contratar: <strong>Esencial</strong>, a $80.000 + IVA con 1.000 mensajes. Cuando un bar necesita más, se le añaden bloques de 1.000 mensajes a $30.000, sin cambiar de plan ni volver a pagar servidor. La medida a la carta es para cadenas y capítulos regionales.</p>
      </div>

      <div class="compare">
        <article class="card rec reveal">
          <span class="badge-rec">★ Recomendada</span>
          <div class="opt-no">OPCIÓN 01</div>
          <h3>Esencial</h3>
          <p class="concept">El plan de entrada, y el único que hay que contratar. Cubre la operación de un bar con consultas de menú, horarios, reservas y pedidos. Si el uso supera el tope, se añaden bloques de mensajes sin cambiar de plan.</p>
          <div class="spec">
            <span class="k">Mensajes incluidos</span>
            <span class="v"><strong>1.000</strong> mensajes al mes</span>
          </div>
          <div class="spec">
            <span class="k">Infraestructura</span>
            <span class="v">Servidor compartido con otros afiliados · 1 slice · respaldos diarios y monitoreo</span>
          </div>
          <div class="spec">
            <span class="k">Costo de IA medido</span>
            <span class="v"><strong>$359</strong> al mes con caché de prompt · <span class="tag">0,4% del precio</span></span>
          </div>
          <div class="risk warn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke-width="2" aria-hidden="true"><circle class="r" cx="12" cy="12" r="9"/><path d="M12 8v5M12 16.5v.5" stroke="#b45309"/></svg>
            <span><strong>Límite:</strong> el servidor se comparte, así que el dimensionamiento depende del conjunto de afiliados. Si el bar supera los 1.000 mensajes, se le avisa y se le ofrecen bloques adicionales antes de facturar cualquier cobro.</span>
          </div>
          <div class="price">
            <div class="price-label">Precio mensual</div>
            <div class="price-amount num">$80.000<span class="price-cur">COP + IVA</span></div>
            <div class="price-note">Factura final con IVA 19%: <span class="num">$95.200</span> · sin permanencia · instalación gratis.</div>
            <div class="price-metrics">
              <div><span class="k">Mensajes incluidos</span><span class="v num">1.000</span></div>
              <div><span class="k">Costo interno</span><span class="v num">$839</span></div>
              <div><span class="k">Bloque adicional</span><span class="v num">$30.000</span></div>
              <div><span class="k">Margen bruto</span><span class="v num">99,0%</span></div>
            </div>
          </div>
          <a class="card-link" href="#detalle-op1">Ver detalle
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>
        </article>

        <article class="card reveal">
          <div class="opt-no">OPCIÓN 02</div>
          <h3>Mensajes adicionales</h3>
          <p class="concept">El plan no cambia: se añaden bloques de 1.000 mensajes cuando el bar los necesita. La infraestructura ya la pagó el plan Esencial, así que el bloque solo cubre su propio consumo.</p>
          <div class="spec">
            <span class="k">Unidad</span>
            <span class="v"><strong>1.000</strong> mensajes por <strong>$30.000</strong> + IVA · se pueden añadir varios bloques al mes</span>
          </div>
          <div class="spec">
            <span class="k">Infraestructura</span>
            <span class="v">Sin costo adicional: la cubre el plan Esencial. El bloque no vuelve a pagar servidor ni instalación.</span>
          </div>
          <div class="spec">
            <span class="k">Costo de IA del bloque</span>
            <span class="v"><strong>$359</strong> por bloque con caché de prompt · <span class="tag">1,2% del precio</span><br><span class="muted-sm">El costo de IA es lineal, así que el margen no se degrada al crecer.</span></span>
          </div>
          <div class="risk ok">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke-width="2" aria-hidden="true"><circle class="r" cx="12" cy="12" r="9"/><path d="M8.5 12.5l2.5 2.5 5-5.5" stroke="#1a7f4e"/></svg>
            <span><strong>Por qué conviene:</strong> el bloque de 1.000 cuesta <strong>$30.000</strong> contra los $80.000 del plan base, porque no repite servidor ni instalación. Es la vía para crecer sin saltar a otro plan.</span>
          </div>
          <div class="price">
            <div class="price-label">Precio por bloque de 1.000</div>
            <div class="price-amount num">$30.000<span class="price-cur">COP + IVA</span></div>
            <div class="price-note">IVA 19%: <span class="num">$35.700</span> final por bloque · se factura solo con aviso previo.</div>
            <div class="price-metrics">
              <div><span class="k">Frente al plan base</span><span class="v num">−63%</span></div>
              <div><span class="k">Costo interno</span><span class="v num">$359</span></div>
              <div><span class="k">Mensajes por bloque</span><span class="v num">1.000</span></div>
              <div><span class="k">Margen bruto</span><span class="v num">98,8%</span></div>
            </div>
          </div>
          <a class="card-link" href="#detalle-op2">Ver detalle
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>
        </article>

        <article class="card muted reveal">
          <div class="opt-no">OPCIÓN 03</div>
          <h3>A la medida</h3>
          <p class="concept">Para cadenas, gastrobares de eventos o capítulos regionales que quieren su propia instancia y control total del consumo.</p>
          <div class="spec">
            <span class="k">Mensajes incluidos</span>
            <span class="v"><strong>Desde 8.000</strong> mensajes al mes, según acuerdo</span>
          </div>
          <div class="spec">
            <span class="k">Infraestructura</span>
            <span class="v">Servidor dedicado al afiliado o al capítulo · talla de <strong>16 a 32 slices</strong> · respaldos y monitoreo a medida</span>
          </div>
          <div class="spec">
            <span class="k">Costo de IA medido</span>
            <span class="v">Facturado al costo real · <span class="tag">transparencia total</span><br><span class="muted-sm">Se entrega el consumo medido desde la tabla <span class="mono">consumo_negocio</span>.</span></span>
          </div>
          <div class="risk warn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke-width="2" aria-hidden="true"><circle class="r" cx="12" cy="12" r="9"/><path d="M12 8v5M12 16.5v.5" stroke="#b45309"/></svg>
            <span><strong>A considerar:</strong> un servidor dedicado cuesta más por negocio que uno compartido. Solo se justifica con volumen alto o con requisitos de aislamiento.</span>
          </div>
          <div class="price">
            <div class="price-label">Precio mensual</div>
            <div class="price-amount is-text">A convenir<span class="price-cur">COP + IVA</span></div>
            <div class="price-note">Se calcula sobre el volumen acordado y la talla de servidor elegida.</div>
            <div class="price-metrics">
              <div><span class="k">Mensajes</span><span class="v">Desde 8.000</span></div>
              <div><span class="k">Costo de IA</span><span class="v">Al costo</span></div>
              <div><span class="k">Bloque adicional</span><span class="v">A convenir</span></div>
              <div><span class="k">Margen bruto</span><span class="v">A calcular</span></div>
            </div>
          </div>
          <a class="card-link" href="#detalle-op3">Ver detalle
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>
        </article>
      </div>

      <div class="topology reveal" aria-label="Arquitectura centralizada del servicio">
        <div class="topo-node a">
          <span class="role">Cliente · WhatsApp</span>
          <span class="hw">El cliente escribe primero</span>
          <span class="job">Abre la ventana de servicio de 24 h</span>
        </div>
        <div class="topo-arrow" aria-hidden="true"><svg width="22" height="16" viewBox="0 0 24 16" fill="none"><path d="M1 8h20M16 2l6 6-6 6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
        <div class="topo-node b">
          <span class="role">Servidor central · 1 slice</span>
          <span class="hw">Una sola instalación atiende a todos</span>
          <span class="job">1,5 GB de RAM · ~50 negocios por núcleo</span>
        </div>
        <div class="topo-arrow" aria-hidden="true"><svg width="22" height="16" viewBox="0 0 24 16" fill="none"><path d="M1 8h20M16 2l6 6-6 6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
        <div class="topo-node c">
          <span class="role">IA · DeepSeek V4.1 Flash</span>
          <span class="hw">Responde en segundos, a cualquier hora</span>
          <span class="job">3.180 tokens de entrada por mensaje</span>
        </div>
      </div>
    </div>
  </section>

  <section id="detalle" style="background:var(--bg-soft);border-top:1px solid var(--line);border-bottom:1px solid var(--line)">
    <div class="wrap">
      <div class="sec-head reveal">
        <div class="sec-kicker">Detalle por modalidad</div>
        <h2 class="sec-title">Qué incluye cada opción y dónde está el riesgo</h2>
        <p class="sec-sub">El costo de IA no es el factor dominante: el servidor cuesta decenas de veces más. La decisión real es cuánta infraestructura dedicar y cuántos mensajes incluir.</p>
      </div>

      <article class="detail rec reveal" id="detalle-op1">
        <div class="dnum num">01</div>
        <div>
          <h3>Esencial · $80.000 + IVA</h3>
          <div class="dsub mono">1.000 mensajes · servidor compartido de 1 slice · instalación gratis</div>
          <p>El plan de entrada, y el único que hay que contratar para empezar. Incluye el agente completo: menú y precios reales, horarios, reservas de mesa, pedidos, escalado a un humano y panel web para el equipo. La instalación, la carga de la carta y la puesta en marcha están incluidas.</p>
          <div class="chips">
            <span class="tag">1.000 mensajes</span>
            <span class="tag">Instalación gratis</span>
            <span class="tag">Sin permanencia</span>
            <span class="tag">Panel web</span>
          </div>
          <ul>
            <li><strong>Costo de operar:</strong> $359 al mes de IA (0,4% del precio base) más $480 de infraestructura prorrateada, para un costo total de $839. El margen bruto es del <strong>99,0%</strong>; si el negocio tuviera que cubrir el servidor completo, bajaría a 84,6%.</li>
            <li><strong>Mensajería de WhatsApp:</strong> sin costo. El agente solo responde dentro de la ventana de servicio de 24 h; nunca envía plantillas de marketing.</li>
            <li><strong>Cuando el bar crece:</strong> los 1.000 mensajes son el tope del plan, pero no un límite duro. Se añaden bloques de 1.000 mensajes a $30.000 + IVA, sin cambiar de plan y sin volver a pagar servidor.</li>
            <li><strong>Instalación:</strong> gratis, en menos de 30 minutos, incluida la carga de la carta y la configuración del tono del agente.</li>
          </ul>
        </div>
      </article>

      <article class="detail reveal" id="detalle-op2">
        <div class="dnum num">02</div>
        <div>
          <h3>Mensajes adicionales · $30.000 + IVA por cada 1.000</h3>
          <div class="dsub mono">Bloques de 1.000 mensajes · sin cambiar de plan · sin volver a pagar servidor</div>
          <p>El bar no cambia de plan cuando crece: se le añaden bloques de 1.000 mensajes a $30.000 + IVA cada uno. La razón del precio es simple: la infraestructura, la instalación y el soporte ya están pagados por el plan Esencial, así que el bloque solo cubre su propio consumo de IA. Por eso el bloque de 1.000 cuesta $30.000 y no los $80.000 del plan base.</p>
          <div class="chips">
            <span class="tag">1.000 mensajes</span>
            <span class="tag">$30.000 por bloque</span>
            <span class="tag">Infraestructura ya cubierta</span>
            <span class="tag">Aviso previo</span>
          </div>
          <ul>
            <li><strong>Costo de operar:</strong> $359 de IA por bloque con caché de prompt, y ningún costo de infraestructura. El margen bruto es del <strong>98,8%</strong> sobre los $30.000.</li>
            <li><strong>El margen no se degrada:</strong> el costo de IA es lineal con el volumen, así que cada bloque mantiene el mismo margen que el anterior. Crecer no diluye la rentabilidad.</li>
            <li><strong>Ejemplo:</strong> 2.000 mensajes al mes son $80.000 + $30.000 = <strong>$110.000</strong> + IVA ($130.900 finales). 3.000 mensajes son $140.000 + IVA ($166.600 finales).</li>
            <li><strong>Política:</strong> nunca se factura un bloque sin aviso. Si el consumo se acerca al tope, el equipo contacta al negocio, le muestra el consumo y le ofrece el bloque; el negocio decide si lo toma o ajusta el uso.</li>
          </ul>
        </div>
      </article>

      <article class="detail reveal" id="detalle-op3">
        <div class="dnum num">03</div>
        <div>
          <h3>A la medida · a convenir</h3>
          <div class="dsub mono">Desde 8.000 mensajes · servidor dedicado de 16 a 32 slices · costo de IA transparente</div>
          <p>Para cadenas de bares, gastrobares de eventos o un capítulo regional completo que quiere su propia instancia, control del consumo y facturación del costo real de IA. El dimensionamiento se calcula con el mismo modelo de tokens que el resto de esta propuesta.</p>
          <div class="chips">
            <span class="tag">Desde 8.000 mensajes</span>
            <span class="tag">16–32 slices</span>
            <span class="tag">Instancia propia</span>
            <span class="tag">Costo de IA al costo</span>
          </div>
          <ul>
            <li><strong>Capacidad:</strong> 16 slices sostienen hasta 400 negocios y 32 slices hasta 800, con 8 y 16 núcleos respectivamente. El límite práctico es la CPU, no la memoria.</li>
            <li><strong>Transparencia:</strong> el consumo se entrega medido por negocio y por día desde la tabla <span class="mono">consumo_negocio</span>, con tokens de entrada, salida y llamadas al LLM.</li>
            <li><strong>Punto de equilibrio:</strong> un servidor dedicado solo se justifica con volumen alto. A 32 slices el costo es de $384.000 al mes, que repartido entre 10 negocios ya son $38.400 por negocio.</li>
            <li><strong>Riesgo:</strong> pagar dedicación sin aprovecharla. La recomendación es empezar compartido y migrar a dedicado cuando el volumen lo exija.</li>
          </ul>
        </div>
      </article>
    </div>
  </section>

  <section id="capacidad">
    <div class="wrap">
      <div class="sec-head reveal">
        <div class="sec-kicker">Infraestructura</div>
        <h2 class="sec-title">Cuántos negocios caben en cada talla</h2>
        <p class="sec-sub">InterServer vende el servidor por <em>slices</em>: cada slice añade recursos de forma predecible. Precios reales publicados, convertidos a una TRM de referencia de $4.000 COP/USD.</p>
      </div>

      <div class="table-scroll reveal">
        <table class="cmp">
          <thead>
            <tr>
              <th>Talla</th><th>Núcleos</th><th>RAM</th><th>SSD</th>
              <th>USD / mes</th><th>COP / mes</th><th>Negocios</th><th>Para qué</th>
            </tr>
          </thead>
          <tbody>
{slices_rows}
          </tbody>
        </table>
      </div>

      <div class="rec-note note-warn reveal">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>
        <span><strong>El límite real es la CPU, no la memoria.</strong> Con el stack centralizado, 1 slice (1 núcleo, 2 GB) ya sostiene ~50 negocios y la RAM permitiría 60. Por eso se escala añadiendo slices por núcleo y no por memoria: cada mensaje es espera de red al modelo (~1,5 s), no cómputo.</span>
      </div>

      <div class="rec-note reveal" style="margin-top:14px">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0f766e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 16v-5M12 8h.01"/></svg>
        <span><strong>Arquitectura centralizada:</strong> una sola instalación atiende a todos los negocios. El aislamiento de datos es lógico, garantizado por <span class="mono">Row Level Security</span> de PostgreSQL: cada fila lleva su <span class="mono">negocio_id</span> y la base filtra por política, el mismo mecanismo que usan los bancos. Aunque la aplicación tuviera un error, la base no devuelve filas de otro negocio. Instalar una copia por bar consumiría ~7 GB y dejaría el servidor al límite de 8 GB.</span>
      </div>
    </div>
  </section>

  <section id="ia" style="background:var(--bg-soft);border-top:1px solid var(--line);border-bottom:1px solid var(--line)">
    <div class="wrap">
      <div class="sec-head reveal">
        <div class="sec-kicker">Costo de IA medido</div>
        <h2 class="sec-title">Cuánto cuesta realmente cada mensaje</h2>
        <p class="sec-sub">El costo se construye de abajo hacia arriba midiendo el código del agente, y se valida contra una conversación de WhatsApp real. Precios oficiales de DeepSeek para <span class="mono">deepseek-flash</span>, tarifa off-peak.</p>
      </div>

      <div class="table-scroll reveal">
        <table class="cmp">
          <thead><tr><th>Componente del prompt</th><th>Origen</th><th>Tokens</th><th>Nota</th></tr></thead>
          <tbody>
{comp_rows}
          </tbody>
        </table>
      </div>

      <div class="rec-note note-warn reveal">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>
        <span><strong>Corrección sobre el cálculo anterior:</strong> el supuesto previo era de 1.630 tokens de entrada por mensaje. Medido, el prompt fijo pesa <strong>2.924</strong> y la entrada real es de ~3.180: casi el doble. Los 1.630 no contaban las 7 herramientas (1.664 tokens) ni el tamaño real del prompt base (1.140, no 900).</span>
      </div>

      <div class="sec-head reveal" style="margin:44px 0 22px">
        <div class="sec-kicker">Verificación</div>
        <h2 class="sec-title" style="font-size:clamp(20px,2.4vw,26px)">Una conversación real, tokenizada</h2>
        <p class="sec-sub">Una conversación de WhatsApp del agente en operación, medida con <span class="mono">tiktoken</span> y simulada turno a turno. Es la primera medición real sobre el agente.</p>
      </div>

      <div class="table-scroll reveal">
        <table class="cmp" style="min-width:640px">
          <thead><tr><th>Métrica</th><th>Medido</th><th>Qué significa</th></tr></thead>
          <tbody>
{medida_rows}
          </tbody>
        </table>
      </div>

      <div class="rec-note reveal">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0f766e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 16v-5M12 8h.01"/></svg>
        <span><strong>El texto del chat no es el costo.</strong> En pantalla la conversación tiene 693 tokens; al modelo se le enviaron <strong>25.394</strong> de entrada, 36,6 veces más. La diferencia es el prompt fijo repetido en cada una de las 8 llamadas, más el historial que se reenvía completo cada vez. Por eso importa el <em>número</em> de mensajes más que su longitud.</span>
      </div>

      <div class="rec-note note-warn reveal" style="margin-top:14px">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>
        <span><strong>La salida real duplica lo estimado.</strong> El modelo asumía 35 tokens de salida por respuesta; la medición da <strong>82</strong>. El agente es conversacional —saluda, usa emoji, lista opciones y recuerda las promociones— así que escribe largo. La entrada del modelo quedó validada con un error de −7,9%, pero la salida estaba subestimada 2,3×. Las cifras de esta propuesta ya usan la corrección.</span>
      </div>

      <div class="sec-head reveal" style="margin:44px 0 22px">
        <div class="sec-kicker">Desglose</div>
        <h2 class="sec-title" style="font-size:clamp(20px,2.4vw,26px)">Costo por perfil de conversación</h2>
        <p class="sec-sub">El historial crece mensaje a mensaje, así que el costo no es lineal: cada turno pesa un poco más que el anterior. El caché de prompt es la diferencia entre las dos columnas de costo.</p>
      </div>

      <div class="table-scroll reveal">
        <table class="cmp">
          <thead><tr><th>Perfil</th><th>Mensajes</th><th>Salida/msg</th><th>Tokens entrada</th><th>Con caché</th><th>Sin caché</th></tr></thead>
          <tbody>
{perfil_rows}
          </tbody>
        </table>
      </div>

      <div class="sec-head reveal" style="margin:44px 0 22px">
        <div class="sec-kicker">Escala</div>
        <h2 class="sec-title" style="font-size:clamp(20px,2.4vw,26px)">El plan de 1.000 mensajes</h2>
        <p class="sec-sub">Según el perfil de conversación que domine en cada bar.</p>
      </div>

      <div class="table-scroll reveal">
        <table class="cmp" style="min-width:720px">
          <thead><tr><th>Perfil dominante</th><th>Conversaciones</th><th>Con caché</th><th>Sin caché</th><th>% de $80.000</th></tr></thead>
          <tbody>
{plan_rows}
          </tbody>
        </table>
      </div>

      <div class="sec-head reveal" style="margin:44px 0 22px">
        <div class="sec-kicker">Sensibilidad</div>
        <h2 class="sec-title" style="font-size:clamp(20px,2.4vw,26px)">Qué pasa si cambian las condiciones</h2>
        <p class="sec-sub">Cada escenario calculado por separado sobre el plan de 1.000 mensajes, no con multiplicadores sueltos.</p>
      </div>

      <div class="table-scroll reveal">
        <table class="cmp" style="min-width:720px">
          <thead><tr><th>Escenario</th><th>Costo mensual</th><th>vs. base</th><th>Condición</th></tr></thead>
          <tbody>
{sens_cols}
          </tbody>
        </table>
      </div>

      <div class="rec-note note-warn reveal">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>
        <span><strong>El riesgo real es perder el caché de prompt.</strong> Todo el modelo depende de que el prefijo de 2.804 tokens se reutilice. Si no ocurre —porque el prompt cambia en cada turno, se reordena el contexto o el proveedor no lo aplica— el costo pasa de $359 a $2.008 al mes. Es el primer supuesto a verificar en el piloto.</span>
      </div>
    </div>
  </section>

  <section id="simulador">
    <div class="wrap">
      <div class="sec-head reveal">
        <div class="sec-kicker">Simulador</div>
        <h2 class="sec-title">Calcula el consumo de un bar</h2>
        <p class="sec-sub">Usa exactamente las mismas constantes que las tablas de arriba: el modelo de tokens medido y los precios reales de DeepSeek e InterServer. Mueve el consumo y el tamaño del servidor.</p>
      </div>

      <div class="sim reveal">
        <div class="sim-panel">
          <label class="sim-label" for="sim-msgs">Mensajes por mes</label>
          <div class="sim-readout"><span id="sim-msgs-out" class="num">1.000</span> <span class="sim-unit">mensajes</span></div>
          <input type="range" id="sim-msgs" min="100" max="8000" step="50" value="1000" aria-label="Mensajes por mes">
          <div class="sim-scale"><span>100</span><span>8.000</span></div>

          <div class="sim-presets">
            <button type="button" class="sim-preset" data-msgs="400">Bar tranquilo<span>400 msgs</span></button>
            <button type="button" class="sim-preset on" data-msgs="1000">Bar activo<span>1.000 msgs</span></button>
            <button type="button" class="sim-preset" data-msgs="3000">Bar de noche<span>3.000 msgs</span></button>
            <button type="button" class="sim-preset" data-msgs="8000">Gastrobar de eventos<span>8.000 msgs</span></button>
          </div>

          <label class="sim-label">Supuesto de caché de prompt</label>
          <div class="sim-toggle" role="group" aria-label="Supuesto de caché de prompt">
            <button type="button" id="sim-cache-on" class="on">Con caché</button>
            <button type="button" id="sim-cache-off">Sin caché</button>
          </div>
          <p class="sim-hint" id="sim-cache-hint">El prefijo de 2.804 tokens se reutiliza: es el mejor caso.</p>

          <label class="sim-label" for="sim-infra" style="margin-top:20px">Tamaño del servidor</label>
          <select id="sim-infra">
            <option value="50" data-costo="12000">1 slice — 50 negocios</option>
            <option value="100" data-costo="24000">2 slices — 100 negocios</option>
            <option value="200" data-costo="96000">8 slices — 200 negocios · soporte gestionado</option>
            <option value="400" data-costo="192000">16 slices — 400 negocios</option>
          </select>

          <label class="sim-label" for="sim-negocios">Negocios en ese servidor</label>
          <div class="sim-readout sim-readout-sm"><span id="sim-negocios-out" class="num">25</span> <span class="sim-unit">negocios</span></div>
          <input type="range" id="sim-negocios" min="1" max="200" step="1" value="25" aria-label="Negocios en el servidor">
          <p class="sim-hint" id="sim-capacidad">Capacidad de este servidor: 50 negocios</p>
        </div>

        <div class="sim-panel sim-result">
          <div class="sim-res-head">
            <span class="sim-res-tag">Factura del negocio</span>
            <div class="sim-big"><span id="sim-factura" class="num">$95.200</span><span class="sim-per">/ mes con IVA</span></div>
            <p class="sim-big-sub" id="sim-factura-sub">Base $80.000 + IVA $15.200</p>
          </div>

          <dl class="sim-rows">
            <div class="sim-row"><dt>Mensajes incluidos</dt><dd id="sim-incluidos">1.000</dd></div>
            <div class="sim-row"><dt>Mensajes adicionales</dt><dd id="sim-excedente">0</dd></div>
            <div class="sim-row sim-row-hi"><dt>Cargo por adicionales</dt><dd id="sim-cargo">$0</dd></div>
            <div class="sim-row sim-sep"><dt>Costo de IA <span class="sim-int">interno</span></dt><dd><span id="sim-ia">$359</span> <span class="sim-sup" id="sim-sup">con caché</span></dd></div>
            <div class="sim-row"><dt>Infraestructura <span class="sim-int">interno</span></dt><dd id="sim-infra-costo">$480</dd></div>
            <div class="sim-row"><dt>Costo total</dt><dd id="sim-costo">$839</dd></div>
            <div class="sim-row sim-row-margen"><dt>Margen bruto</dt><dd><span id="sim-margen">$79.161</span> <span class="sim-pct" id="sim-margen-pct">99,0%</span></dd></div>
          </dl>

          <div class="sim-bar">
            <span class="sim-bar-lbl">Composición del precio base</span>
            <div class="sim-bar-track"><span class="sim-bar-fill" id="sim-bar-fill"></span></div>
            <div class="sim-bar-legend">
              <span><i class="sw sw-margen"></i>Margen <b id="sim-leg-margen">99,0%</b></span>
              <span><i class="sw sw-ia"></i>IA <b id="sim-leg-ia">0,4%</b></span>
              <span><i class="sw sw-infra"></i>Infra <b id="sim-leg-infra">0,6%</b></span>
            </div>
          </div>
        </div>
      </div>

      <div id="sim-aviso" class="rec-note note-warn" hidden>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>
        <span id="sim-aviso-txt"></span>
      </div>

      <div class="rec-note reveal" style="margin-top:14px">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0f766e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 16v-5M12 8h.01"/></svg>
        <span><strong>Cómo se calcula.</strong> La IA se cobra por token, no por mensaje: 1.630 tokens de entrada y 35 de salida por mensaje en el modelo original; tras la medición, el prompt fijo es de 2.924 tokens (del que 2.804 es prefijo cacheable) y la salida real es de 82. Los mensajes por encima de los 1.000 incluidos se cobran en bloques de 1.000 a <span class="mono">$30.000</span> cada uno. La infraestructura es el costo del servidor dividido entre los negocios que aloja. El IVA se muestra aparte porque se traslada a la DIAN y no es ingreso.</span>
      </div>
    </div>
  </section>

  <section id="comparativa" style="background:var(--bg-soft);border-top:1px solid var(--line)">
    <div class="wrap">
      <div class="sec-head reveal">
        <div class="sec-kicker">Comparativa</div>
        <h2 class="sec-title">El plan, los bloques y la medida, lado a lado</h2>
        <p class="sec-sub">El plan Esencial incluye el agente completo y la instalación gratis. Los bloques de mensajes se suman sobre el plan. La medida a la carta cambia la infraestructura.</p>
      </div>

      <div class="table-scroll reveal">
        <table class="cmp">
          <thead>
            <tr>
              <th>Concepto</th>
              <th class="col-rec">Esencial ★</th>
              <th>Mensajes adicionales</th>
              <th>A la medida</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="rowhead">Precio</td>
              <td class="num col-rec"><span class="strong">$80.000</span></td>
              <td class="num"><span class="strong">$30.000</span></td>
              <td class="num">A convenir</td>
            </tr>
            <tr>
              <td class="rowhead">Unidad de cobro</td>
              <td class="col-rec">Mensual</td>
              <td>Por cada 1.000 mensajes</td>
              <td>Según acuerdo</td>
            </tr>
            <tr>
              <td class="rowhead">IVA 19%</td>
              <td class="num col-rec">$15.200</td>
              <td class="num">$5.700</td>
              <td class="num">—</td>
            </tr>
            <tr>
              <td class="rowhead">Valor final con IVA</td>
              <td class="num col-rec"><span class="strong">$95.200</span></td>
              <td class="num"><span class="strong">$35.700</span></td>
              <td class="num">—</td>
            </tr>
            <tr>
              <td class="rowhead">Mensajes</td>
              <td class="num col-rec">1.000 incluidos</td>
              <td class="num"><span class="strong">1.000</span> por bloque</td>
              <td class="num">Desde 8.000</td>
            </tr>
            <tr>
              <td class="rowhead">Precio por 1.000 mensajes</td>
              <td class="num col-rec">$80.000</td>
              <td class="num"><span class="strong">$30.000</span> <span class="muted-sm">−63%</span></td>
              <td class="num">A convenir</td>
            </tr>
            <tr>
              <td class="rowhead">Costo de IA</td>
              <td class="num col-rec">$359</td>
              <td class="num">$359 por bloque</td>
              <td class="muted-sm">Al costo real</td>
            </tr>
            <tr>
              <td class="rowhead">Infraestructura</td>
              <td class="col-rec">Compartida · 1 slice</td>
              <td>Ya cubierta por el plan base</td>
              <td>Dedicada · 16–32 slices</td>
            </tr>
            <tr>
              <td class="rowhead">Costo total interno</td>
              <td class="num col-rec">$839</td>
              <td class="num">$359</td>
              <td class="num">A calcular</td>
            </tr>
            <tr>
              <td class="rowhead">Capacidad del servidor</td>
              <td class="num col-rec">50 negocios</td>
              <td class="num">La del plan base</td>
              <td class="num">400–800 negocios</td>
            </tr>
            <tr>
              <td class="rowhead">Margen bruto</td>
              <td class="num col-rec"><span class="strong">99,0%</span></td>
              <td class="num"><span class="strong">98,8%</span></td>
              <td class="num">A calcular</td>
            </tr>
            <tr>
              <td class="rowhead">Instalación</td>
              <td class="col-rec"><span class="tag">Gratis</span></td>
              <td class="muted-sm">No aplica</td>
              <td><span class="tag">Gratis</span></td>
            </tr>
            <tr>
              <td class="rowhead">Permanencia</td>
              <td class="col-rec">Ninguna</td>
              <td>Según consumo</td>
              <td>Según acuerdo</td>
            </tr>
            <tr>
              <td class="rowhead">Para quién</td>
              <td class="col-rec muted-sm">El plan que contrata cualquier bar</td>
              <td class="muted-sm">El bar que superó los 1.000 mensajes del plan</td>
              <td class="muted-sm">Cadenas y capítulos regionales</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="rec-note reveal">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0f766e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 16v-5M12 8h.01"/></svg>
        <span><strong>Recomendación:</strong> contratar el <strong>plan Esencial</strong> y crecer por bloques. Es la estructura más simple de vender y la más fácil de presupuestar para el bar: un precio fijo de $80.000 al mes y, cuando el uso lo pida, bloques de 1.000 mensajes a $30.000. La razón económica es que el bloque de 1.000 cuesta <strong>$30.000</strong> contra los $80.000 del plan base, porque la infraestructura, la instalación y el soporte ya están pagados; y como el costo de IA es lineal con el volumen, cada bloque mantiene un margen del <strong>98,8%</strong> sin degradarse. La Opción 03 solo se justifica cuando hay un requisito de aislamiento o un volumen que sature un servidor compartido.</span>
      </div>

      <div class="rec-note note-warn reveal" style="margin-top:14px">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>
        <span><strong>Pendiente antes de fijar precios definitivos:</strong> estas cifras son un modelo construido sobre el código del agente y validado con una conversación real, no una factura. La tabla <span class="mono">consumo_negocio</span> ya registra tokens de entrada, salida y llamadas por negocio y día, pero aún no se ha leído con datos de un piloto completo. Los precios del plan Esencial y de los bloques de mensajes son una recomendación derivada del modelo, no una tarifa ya validada en operación.</span>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="wrap foot">
    <span>Agente de WhatsApp con IA · AsoBares — operado por Purosesu Labs</span>
    <span class="mono">Purosesu-Labs/precios-riv</span>
  </div>
</footer>

<script>{dither_js(TEAL)}</script>
<script>{SIM_JS}</script>
<script>
(function(){{
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var reveals = document.querySelectorAll(".reveal");
  if (reduce || !("IntersectionObserver" in window)) {{
    reveals.forEach(function(el){{ el.classList.add("in"); }});
  }} else {{
    var io = new IntersectionObserver(function(entries){{
      entries.forEach(function(e){{
        if (e.isIntersecting){{ e.target.classList.add("in"); io.unobserve(e.target); }}
      }});
    }}, {{threshold: 0.12, rootMargin: "0px 0px -40px 0px"}});
    reveals.forEach(function(el){{ io.observe(el); }});
  }}
}})();
</script>
</body>
</html>
'''

assert MENSAJES_INCLUIDOS == 1000
assert PRECIO_FINAL == 95200

out_path = os.path.join(OUT, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_doc)

print(f"OK · {out_path}")
print(f"   {len(html_doc):,} bytes · Compare con 3 modalidades")
print(f"   Precio base ${PRECIO_BASE:,} + IVA ${PRECIO_IVA:,} = ${PRECIO_FINAL:,}")
