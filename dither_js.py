# -*- coding: utf-8 -*-
"""Dither Canvas (ObsidianUI) — implementación compartida y parametrizable.

Réplica fiel del efecto original (obsidianui.dev/docs/dither-canvas):

  · superficie blanca **opaca** (alpha:false, clearColor blanco), como el original
  · rejilla fina de caracteres sobre atlas monoespaciado (110 columnas)
  · matriz de Bayer 4x4 como umbral → la densidad de glifos forma la imagen
  · simulación de fluido (diffuse → project → advect) que distorsiona con el puntero
  · conjunto de glifos en dos familias: bordes (.,=+-) y brillos (letras de marca)

Lo único que cambia respecto al original es la fuente de la señal. El original
anima un <video> y usa su luminancia; aquí el proyecto no cuenta con ese video,
así que la señal se genera proceduralmente con ruido value-fBm, domain warping
y bandas direccionales. El resto del pipeline es idéntico.

Se degrada en silencio si no hay WebGL2 o si el shader falla: el canvas queda
en opacidad 0 y se ve el fallback CSS con mask-image.
"""
import json

# --------------------------------------------------------------------------
# Paletas: (base, matiz, flujo, acento). Valores 0..1 para el shader.
# --------------------------------------------------------------------------
TEAL = {
    "a": (0.059, 0.463, 0.431),   # teal del sistema de propuestas comerciales
    "b": (0.051, 0.580, 0.529),   # matiz claro hacia la derecha
    "c": (0.043, 0.369, 0.345),   # oscurece donde empuja el flujo
    "d": (0.102, 0.498, 0.306),   # acento verde al borde derecho
}

INDIGO = {
    "a": (0.145, 0.388, 0.922),   # azul del sistema Stripi
    "b": (0.020, 0.640, 0.880),   # cian
    "c": (0.360, 0.290, 0.950),   # violeta donde empuja el flujo
    "d": (0.917, 0.133, 0.380),   # rubí al borde derecho
}

FC = 80          # columnas de la rejilla de fluido
FR = 60          # filas de la rejilla de fluido
TM = 72          # máximo de puntos de estela del puntero
BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]

VS = "#version 300 es\nin vec2 a_pos;\nvoid main(){ gl_Position = vec4(a_pos, 0, 1); }"


def _unique(text):
    """Letras de marca sin repetir: 'ASOBARES' -> A,S,O,B,R,E."""
    seen, out = set(), []
    for ch in text:
        if ch not in seen:
            seen.add(ch)
            out.append(ch)
    return out


def _fragment_shader(edges, brights, pal, side_lo=1.0):
    """Shader de fragmento. Sin f-strings: el GLSL usa llaves en bucles."""
    bayer = ",".join(str(round(v / 16 * 255)) for v in BAYER)
    c = lambda k: ", ".join("%.3f" % v for v in pal[k])
    n_edges = str(len(edges))
    n_brights = str(len(brights))
    chars = str(len(edges) + len(brights))

    return "\n".join([
        "#version 300 es",
        "precision highp float;",
        "uniform sampler2D uFluid, uAtlas;",
        "uniform vec2 uRes;",
        "uniform float uCC;",
        "uniform float uTime;",
        "uniform int uPhase, uTrailN;",
        "uniform vec4 uTP[" + str(TM) + "];",
        "uniform float uTL[" + str(TM) + "];",
        "out vec4 O;",
        "const float EL = 36.0, EH = 130.0;",
        "const float FC = " + str(FC) + ".0, FR = " + str(FR) + ".0;",
        "const int BAYER[16] = int[16](" + bayer + ");",
        "const int EDGE_N = " + n_edges + ", BRIGHT_N = " + n_brights + ";",
        "const int CHAR_N = " + chars + ";",
        "",
        "/* --- Señal procedural: sustituye a la luminancia del video original --- */",
        "float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }",
        "float vnoise(vec2 p){",
        "  vec2 i = floor(p), f = fract(p);",
        "  vec2 u = f * f * (3.0 - 2.0 * f);",
        "  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),",
        "             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);",
        "}",
        "float fbm(vec2 p){",
        "  float v = 0.0, a = 0.5;",
        "  for(int i = 0; i < 5; i++){ v += a * vnoise(p); p = p * 2.03 + 17.7; a *= 0.5; }",
        "  return v;",
        "}",
        "float signal(vec2 uv){",
        "  vec2 q = uv * vec2(2.3, 1.7);",
        "  float t = uTime * 0.06;",
        "  vec2 w = vec2(fbm(q + vec2(t, 4.1)), fbm(q + vec2(9.3, -t)));",
        "  /* dos escalas de estructura: masas grandes y detalle fino */",
        "  float macro = smoothstep(0.34, 0.66, fbm(q + w * 2.2));",
        "  float micro = smoothstep(0.25, 0.80, fbm(q * 3.1 - w * 1.4));",
        "  float n = clamp(macro * 0.78 + micro * 0.34, 0.0, 1.0);",
        "  float bandA = sin((uv.x * 3.1 + uv.y * 2.2) * 3.141592 + uTime * 0.35) * 0.5 + 0.5;",
        "  float bandB = sin((uv.y * 4.3 - uv.x * 1.7) * 3.141592 - uTime * 0.27) * 0.5 + 0.5;",
        "  float s = n * (0.70 + 0.20 * bandA + 0.14 * bandB);",
        "  float band = smoothstep(0.0, 1.0, clamp(1.0 - abs(uv.y - 0.46) * 1.05, 0.0, 1.0));",
        "  float edge = smoothstep(0.015, 0.22, uv.y) * (1.0 - smoothstep(0.82, 1.0, uv.y));",
        "  /* Sesgo de lado: la masa densa se concentra a la derecha para que el",
        "     titular de la izquierda no dependa del fotograma. */",
        "  float side = mix(" + ("%.3f" % side_lo) + ", 1.0, smoothstep(0.08, 0.90, uv.x));",
        "  return clamp(s * (0.34 + 0.66 * band) * mix(0.30, 1.0, edge) * side * 1.45, 0.0, 1.0);",
        "}",
        "",
        "void main(){",
        "  float cw = uRes.x / uCC;",
        "  float rows = ceil(uRes.y / cw) + 1.0;",
        "  float gx = floor(gl_FragCoord.x / cw);",
        "  float gy = floor((uRes.y - gl_FragCoord.y) / cw);",
        "  if(gx >= uCC || gy >= rows) discard;",
        "  vec2 cp = vec2(fract(gl_FragCoord.x / cw), fract((uRes.y - gl_FragCoord.y) / cw));",
        "  vec2 bp = vec2((gx + 0.5) * cw, (gy + 0.5) * cw);",
        "  ivec2 fc = ivec2(gx / uCC * FC, gy / rows * FR);",
        "  fc = clamp(fc, ivec2(0), ivec2(int(FC) - 1, int(FR) - 1));",
        "  vec2 flow = texelFetch(uFluid, fc, 0).rg;",
        "",
        "  /* estela del puntero: empuja la celda y la desplaza */",
        "  vec2 disp = vec2(0.0);",
        "  for(int i = 0; i < uTrailN; i++){",
        "    float life = uTL[i];",
        "    if(life <= 0.0) continue;",
        "    vec2 d = bp - uTP[i].xy;",
        "    float dist = length(d);",
        "    float r = 5.0 + life * 3.0;",
        "    if(dist == 0.0 || dist > r) continue;",
        "    float f = pow(1.0 - dist / r, 2.0);",
        "    disp += (d / dist) * f * life * 3.0 + uTP[i].zw * f * 0.04;",
        "  }",
        "",
        "  vec2 sp = bp + disp + flow * 6.0;",
        "  vec2 uv = clamp(sp / uRes, 0.0, 1.0);",
        "  float s = signal(uv);",
        "",
        "  /* luminancia → umbral de Bayer. La densidad de glifos forma la imagen. */",
        "  float bg = smoothstep(0.14, 0.90, s) * 255.0;",
        "  float hm = min(1.0, length(flow) * 1.1);",
        "  float gray = bg * (1.0 - hm) + (255.0 - bg) * hm;",
        "  float thr = float(BAYER[(int(gy) & 3) * 4 + (int(gx) & 3)]);",
        "  bool invDark = hm > 0.05 && bg > thr && gray <= thr;",
        "  bool lit = gray > thr;",
        "  if(!lit && !invDark) discard;",
        "",
        "  /* elección de glifo: bordes para medios tonos, letras para las luces */",
        "  float pg = invDark ? bg : gray;",
        "  int ci;",
        "  if(pg >= EL && pg <= EH) ci = uPhase % EDGE_N;",
        "  else if(pg > EH) ci = EDGE_N + uPhase % BRIGHT_N;",
        "  else discard;",
        "",
        "  float au = (float(ci) + cp.x) / float(CHAR_N);",
        "  float ca = texture(uAtlas, vec2(au, cp.y)).a;",
        "  if(ca < 0.05) discard;",
        "",
        "  vec3 colA = vec3(" + c("a") + ");",
        "  vec3 colB = vec3(" + c("b") + ");",
        "  vec3 colC = vec3(" + c("c") + ");",
        "  vec3 colD = vec3(" + c("d") + ");",
        "  float tint = smoothstep(0.15, 0.9, uv.x * 0.6 + uv.y * 0.4);",
        "  vec3 col = mix(colA, colB, tint);",
        "  col = mix(col, colC, hm * 0.65);",
        "  col = mix(col, colD, smoothstep(0.72, 1.0, uv.x) * 0.45);",
        "  float a = (invDark ? 0.85 : 1.0) * ca;",
        "  O = vec4(col * a, a);",
        "}",
    ])


_JS = r"""
/* Dither Canvas — ObsidianUI (obsidianui.dev/docs/dither-canvas).
   Fiel al original salvo la fuente de la señal: aquí es procedural (ruido fBm
   con domain warping y bandas direccionales) porque el proyecto no cuenta con
   el video. Se conserva todo el pipeline: superficie blanca opaca, rejilla de
   caracteres, matriz de Bayer 4x4, simulación de fluido y distorsión por puntero.
   Se degrada en silencio si no hay WebGL2, dejando visible el fallback CSS. */
(function(){
"use strict";
var canvas = document.getElementById(__ELEMENT__);
if (!canvas) return;
var motion = window.matchMedia('(prefers-reduced-motion: reduce)');

var FC = __FC__, FR = __FR__, FN = FC * FR;
var CELL = __CELL__;
var EDGES = __EDGES__;
var BRIGHTS = __BRIGHTS__;
var ALL_CHARS = EDGES.concat(BRIGHTS);
var BAYER = __BAYER__;
var TL = 320, TS = 10, TM = __TM__;
var TRAIL_CFG = { fb: 0.08, fss: 18, ffm: 0.15, fir: 0.8, firl: 1.0 };

var VS = __VS__;
var FS = __FS__;

function createFluid(){
  var vx = new Float32Array(FN), vy = new Float32Array(FN);
  var vx0 = new Float32Array(FN), vy0 = new Float32Array(FN);
  var p = new Float32Array(FN), div = new Float32Array(FN);
  function fi(x, y){
    return Math.max(0, Math.min(FR - 1, y)) * FC + Math.max(0, Math.min(FC - 1, x));
  }
  function bnd(b, a){
    var x, y;
    for (x = 1; x < FC - 1; x++){
      a[fi(x, 0)] = b === 2 ? -a[fi(x, 1)] : a[fi(x, 1)];
      a[fi(x, FR - 1)] = b === 2 ? -a[fi(x, FR - 2)] : a[fi(x, FR - 2)];
    }
    for (y = 1; y < FR - 1; y++){
      a[fi(0, y)] = b === 1 ? -a[fi(1, y)] : a[fi(1, y)];
      a[fi(FC - 1, y)] = b === 1 ? -a[fi(FC - 2, y)] : a[fi(FC - 2, y)];
    }
  }
  function diffuse(b, d, s, diff, dt){
    var a = dt * diff * FN, k, x, y;
    for (k = 0; k < 4; k++){
      for (y = 1; y < FR - 1; y++) for (x = 1; x < FC - 1; x++){
        d[fi(x, y)] = (s[fi(x, y)] + a * (d[fi(x-1,y)] + d[fi(x+1,y)] + d[fi(x,y-1)] + d[fi(x,y+1)])) / (1 + 4 * a);
      }
      bnd(b, d);
    }
  }
  function advect(b, d, d0, ux, uy, dt){
    var dtx = dt * FC * 1.4, dty = dt * FR * 1.4, x, y;
    for (y = 1; y < FR - 1; y++) for (x = 1; x < FC - 1; x++){
      var px = Math.max(0.5, Math.min(FC - 1.5, x - dtx * ux[fi(x, y)]));
      var py = Math.max(0.5, Math.min(FR - 1.5, y - dty * uy[fi(x, y)]));
      var x0 = Math.floor(px), y0 = Math.floor(py);
      var s1 = px - x0, s0 = 1 - s1, t1 = py - y0, t0 = 1 - t1;
      d[fi(x, y)] = s0 * (t0 * d0[fi(x0,y0)] + t1 * d0[fi(x0,y0+1)]) + s1 * (t0 * d0[fi(x0+1,y0)] + t1 * d0[fi(x0+1,y0+1)]);
    }
    bnd(b, d);
  }
  function project(ux, uy){
    var hx = 1 / FC, hy = 1 / FR, k, x, y;
    for (y = 1; y < FR - 1; y++) for (x = 1; x < FC - 1; x++){
      div[fi(x,y)] = -0.5 * (hx * (ux[fi(x+1,y)] - ux[fi(x-1,y)]) + hy * (uy[fi(x,y+1)] - uy[fi(x,y-1)]));
      p[fi(x,y)] = 0;
    }
    bnd(0, div); bnd(0, p);
    for (k = 0; k < 4; k++){
      for (y = 1; y < FR - 1; y++) for (x = 1; x < FC - 1; x++){
        p[fi(x,y)] = (div[fi(x,y)] + p[fi(x-1,y)] + p[fi(x+1,y)] + p[fi(x,y-1)] + p[fi(x,y+1)]) / 4;
      }
      bnd(0, p);
    }
    for (y = 1; y < FR - 1; y++) for (x = 1; x < FC - 1; x++){
      ux[fi(x,y)] -= 0.5 * (p[fi(x+1,y)] - p[fi(x-1,y)]) / hx;
      uy[fi(x,y)] -= 0.5 * (p[fi(x,y+1)] - p[fi(x,y-1)]) / hy;
    }
    bnd(1, ux); bnd(2, uy);
  }
  return {
    vx: vx, vy: vy, fi: fi,
    step: function(){
      diffuse(1, vx0, vx, 0.00002, 0.016);
      diffuse(2, vy0, vy, 0.00002, 0.016);
      project(vx0, vy0);
      advect(1, vx, vx0, vx0, vy0, 0.016);
      advect(2, vy, vy0, vx0, vy0, 0.016);
      project(vx, vy);
      for (var i = 0; i < FN; i++){ vx[i] *= 0.94; vy[i] *= 0.94; }
    }
  };
}

/* Autodisparo: sin puntero, la simulación recibe impulsos periódicos para que
   la textura nunca quede muerta. */
function autoPulse(fluid, W, H){
  var cx = ((0.28 + Math.random() * 0.44) * W) | 0;
  var cy = ((0.25 + Math.random() * 0.5) * H) | 0;
  var ang = Math.random() * Math.PI * 2;
  var mag = 1.6 + Math.random() * 2.4;
  var vx = Math.cos(ang) * mag, vy = Math.sin(ang) * mag;
  var r = 9;
  var gx = ((cx / W) * FC) | 0, gy = ((cy / H) * FR) | 0;
  for (var dy = -r; dy <= r; dy++) for (var dx = -r; dx <= r; dx++){
    var dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > r) continue;
    var f = Math.pow(1 - dist / r, 2);
    fluid.vx[fluid.fi(gx + dx, gy + dy)] += vx * f * 2.2;
    fluid.vy[fluid.fi(gx + dx, gy + dy)] += vy * f * 2.2;
  }
}

var gl = null;
try {
  /* alpha:false como el original: superficie blanca opaca, sin velo encima. */
  gl = canvas.getContext('webgl2', { alpha: false, antialias: false, premultipliedAlpha: true, preserveDrawingBuffer: true });
} catch (e) { gl = null; }
if (!gl) return;   /* el fallback CSS con mask-image queda visible */

var disposed = false, rafId = 0, textures = [], shaders = [], buffers = [], prog = null;
var listeners = [];

function cleanup(){
  if (disposed) return;
  disposed = true;
  cancelAnimationFrame(rafId);
  listeners.forEach(function (off) { off(); });
  textures.forEach(function (t) { gl.deleteTexture(t); });
  buffers.forEach(function (b) { gl.deleteBuffer(b); });
  shaders.forEach(function (s) { gl.deleteShader(s); });
  if (prog) gl.deleteProgram(prog);
}
function listen(target, event, handler){
  target.addEventListener(event, handler);
  listeners.push(function () { target.removeEventListener(event, handler); });
}
function fallback(){
  if (disposed) return;
  canvas.style.opacity = '0';
  canvas.style.pointerEvents = 'none';
  cleanup();
}
/* Reporta el motivo una sola vez: un fallo mudo de shader es imposible de depurar. */
function reportar(motivo){
  if (window.__ditherDiag) return;
  window.__ditherDiag = String(motivo);
  if (window.console && console.warn) console.warn('[dither-canvas] desactivado:', motivo);
}

try {
  function mkShader(type, source){
    var sh = gl.createShader(type);
    if (!sh) throw new Error('shader alloc');
    shaders.push(sh);
    gl.shaderSource(sh, source);
    gl.compileShader(sh);
    if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
      throw new Error('shader compile: ' + (gl.getShaderInfoLog(sh) || 'sin log'));
    }
    return sh;
  }
  function mkTex(unit){
    var tex = gl.createTexture();
    if (!tex) throw new Error('tex alloc');
    textures.push(tex);
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return tex;
  }

  prog = gl.createProgram();
  if (!prog) throw new Error('prog alloc');
  gl.attachShader(prog, mkShader(gl.VERTEX_SHADER, VS));
  gl.attachShader(prog, mkShader(gl.FRAGMENT_SHADER, FS));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error('link');
  gl.useProgram(prog);

  function loc(name){ return gl.getUniformLocation(prog, name); }

  var buf = gl.createBuffer();
  if (!buf) throw new Error('buf alloc');
  buffers.push(buf);
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  var aPos = gl.getAttribLocation(prog, 'a_pos');
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  var fluidTex = mkTex(0);

  var atlasCanvas = document.createElement('canvas');
  var CELL = 64;
  atlasCanvas.width = CELL * ALL_CHARS.length;
  atlasCanvas.height = CELL;
  var actx = atlasCanvas.getContext('2d');
  if (!actx) throw new Error('atlas');
  actx.font = (CELL * 0.92) + 'px monospace';
  actx.textAlign = 'center';
  actx.textBaseline = 'middle';
  actx.fillStyle = '#fff';
  ALL_CHARS.forEach(function (ch, i) { actx.fillText(ch, CELL * (i + 0.5), CELL * 0.5); });
  mkTex(1);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, atlasCanvas);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.uniform1i(loc('uFluid'), 0);
  gl.uniform1i(loc('uAtlas'), 1);

  var fluid = createFluid();
  var fluidData = new Float32Array(FN * 2);
  var mouse = { x: -9999, y: -9999, vx: 0, vy: 0 };
  var trail = [];
  function now(){ return performance.now(); }

  function onMove(ev){
    var rect = canvas.getBoundingClientRect();
    var px = mouse.x, py = mouse.y;
    mouse.x = ev.clientX - rect.left;
    mouse.y = ev.clientY - rect.top;
    mouse.vx = mouse.x - px;
    mouse.vy = mouse.y - py;
    if (px < 0 || py < 0){
      trail.unshift({ x: mouse.x, y: mouse.y, vx: 0, vy: 0, b: now() });
      if (trail.length > TM) trail.length = TM;
      return;
    }
    var d = Math.sqrt(mouse.vx * mouse.vx + mouse.vy * mouse.vy);
    if (d < 0.5) return;
    var steps = Math.max(1, Math.ceil(d / TS));
    var birth = now();
    for (var s = 1; s <= steps; s++){
      var t = s / steps;
      trail.unshift({ x: px + mouse.vx * t, y: py + mouse.vy * t, vx: mouse.vx / steps, vy: mouse.vy / steps, b: birth });
      if (trail.length > TM) trail.length = TM;
    }
  }
  listen(canvas, 'pointermove', onMove);
  listen(canvas, 'pointerleave', function () { mouse.x = mouse.y = -9999; });
  listen(canvas, 'webglcontextlost', function (ev) { ev.preventDefault(); fallback(); });

  var W = 1, H = 1;
  /* Columnas según el ancho, no un número fijo: con un ancho estrecho (la
     columna de documentación) un número fijo de columnas daría glifos
     diminutos y el efecto se leería como polvo en vez de textura. */
  function resize(){
    var rect = canvas.getBoundingClientRect();
    W = canvas.width = Math.max(1, Math.round(rect.width));
    H = canvas.height = Math.max(1, Math.round(rect.height));
    gl.viewport(0, 0, W, H);
    var cc = Math.round(W / CELL);
    gl.uniform1f(uCC, Math.max(34, Math.min(142, cc)));
  }
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

  var uTP = loc('uTP'), uTLoc = loc('uTL'), uRes = loc('uRes');
  var uPhase = loc('uPhase'), uTrailN = loc('uTrailN'), uTime = loc('uTime');
  var uCC = loc('uCC');

  resize();
  var tpBuf = new Float32Array(TM * 4);
  var tlBuf = new Float32Array(TM);
  var phase = 0, frame = 0, pulseAt = 0, running = false;
  var t0 = now();

  function draw(){
    var ts = now();
    var elapsed = (ts - t0) / 1000;
    var cfg = TRAIL_CFG;

    /* impulsos automáticos para que el campo nunca quede estático */
    if (ts - pulseAt > 900){
      pulseAt = ts;
      autoPulse(fluid, W, H);
    }

    for (var i = trail.length - 1; i >= 0; i--){
      var pt = trail[i];
      var age = ts - pt.b;
      if (age >= TL){ trail.splice(i, 1); continue; }
      var life = 1 - age / TL;
      var radius = cfg.fir + life * cfg.firl;
      var gr = Math.ceil(radius);
      var speed = Math.sqrt(pt.vx * pt.vx + pt.vy * pt.vy);
      var force = (cfg.fb + Math.min(speed, cfg.fss) / cfg.fss) * life;
      var cx = ((pt.x / W) * FC) | 0;
      var cy = ((pt.y / H) * FR) | 0;
      for (var dy = -gr; dy <= gr; dy++) for (var dx = -gr; dx <= gr; dx++){
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > radius) continue;
        var f = Math.pow(1 - dist / radius, 2);
        fluid.vx[fluid.fi(cx + dx, cy + dy)] += pt.vx * f * force * cfg.ffm;
        fluid.vy[fluid.fi(cx + dx, cy + dy)] += pt.vy * f * force * cfg.ffm;
      }
    }

    fluid.step();
    if (frame++ % 8 === 0) phase = (phase + 1) % 255;

    for (var j = 0; j < FN; j++){
      fluidData[j * 2] = fluid.vx[j];
      fluidData[j * 2 + 1] = fluid.vy[j];
    }
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, fluidTex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RG32F, FC, FR, 0, gl.RG, gl.FLOAT, fluidData);

    tpBuf.fill(0); tlBuf.fill(0);
    for (var k = 0; k < trail.length; k++){
      var q = trail[k];
      tpBuf[k*4] = q.x; tpBuf[k*4+1] = q.y; tpBuf[k*4+2] = q.vx; tpBuf[k*4+3] = q.vy;
      tlBuf[k] = 1 - (ts - q.b) / TL;
    }
    gl.uniform4fv(uTP, tpBuf);
    gl.uniform1fv(uTLoc, tlBuf);
    gl.uniform1i(uTrailN, trail.length);
    gl.uniform2f(uRes, W, H);
    gl.uniform1i(uPhase, phase);
    gl.uniform1f(uTime, elapsed);
    gl.clearColor(1, 1, 1, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    if (canvas.style.opacity !== '1') canvas.style.opacity = '1';
  }

  function render(){
    if (disposed || !running) return;
    try { draw(); } catch (e) { fallback(); return; }
    rafId = requestAnimationFrame(render);
  }

  /* Solo anima mientras la banda es visible: sin costo fuera de pantalla. */
  function start(){
    if (disposed || running) return;
    /* Con movimiento reducido se pinta un fotograma estático y se detiene.
       preserveDrawingBuffer mantiene ese fotograma visible. */
    if (motion.matches) { try { draw(); } catch (e) { reportar(e && e.message ? e.message : e); fallback(); } return; }
    running = true;
    rafId = requestAnimationFrame(render);
  }
  function stop(){
    running = false;
    cancelAnimationFrame(rafId);
  }

  listen(motion, 'change', function () { stop(); start(); });

  if ('IntersectionObserver' in window){
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) start(); else stop(); });
    }, { threshold: 0.01 });
    io.observe(canvas);
    listeners.push(function () { io.disconnect(); });
  } else {
    start();
  }

  var ro = new ResizeObserver(function () { resize(); if (!running) { try { draw(); } catch (e) {} } });
  ro.observe(canvas.parentElement);
  listeners.push(function () { ro.disconnect(); });

} catch (e) {
  reportar(e && e.message ? e.message : e);
  fallback();
}
})();
"""


def dither_js(palette=TEAL, cell=13.0, brights="ASOBRES",
              edges=(".", ",", "=", "+", "-"), element="dither", side_lo=0.35):
    """Devuelve el JS del Dither Canvas listo para incrustar en un <script>.

    palette  : TEAL o INDIGO
    cell     : lado de la celda de carácter en px CSS. El número de columnas se
               deriva del ancho del canvas, así el glifo mide igual en una banda
               ancha (portada) y en una estrecha (columna de documentación).
    brights  : letras que se usan en las zonas más luminosas (se deduplican)
    edges    : glifos para los medios tonos
    element  : id del <canvas> en la página
    side_lo  : densidad relativa en el borde izquierdo. < 1 deja la izquierda
               más limpia (donde va el titular); 1.0 reparte por igual.
    """
    edge_list = list(edges)
    bright_list = _unique(brights)
    fs = _fragment_shader(edge_list, bright_list, palette, side_lo)

    js = _JS
    for token, value in (
        ("__ELEMENT__", json.dumps(element)),
        ("__FC__", str(FC)),
        ("__FR__", str(FR)),
        ("__TM__", str(TM)),
        ("__CELL__", "%g" % cell),
        ("__EDGES__", json.dumps(edge_list)),
        ("__BRIGHTS__", json.dumps(bright_list)),
        ("__BAYER__", json.dumps(BAYER)),
        ("__VS__", json.dumps(VS)),
        ("__FS__", json.dumps(fs)),
    ):
        js = js.replace(token, value)
    return js
