# -*- coding: utf-8 -*-
"""JS del Dither Canvas (ObsidianUI), adaptado a la paleta teal de la propuesta.

Separado del generador para que las llaves de JavaScript no colisionen con
las del f-string que arma el HTML. Sin el video original: la senal se genera
proceduralmente y conserva el pipeline completo (simulacion de fluido,
matriz de Bayer 4x4, atlas de caracteres, distorsion por puntero).
"""

DITHER_JS = r"""
/* Dither Canvas — adaptado de ObsidianUI (obsidianui.dev/docs/dither-canvas).
   Sin el video original: la señal se genera proceduralmente y se le aplica el
   mismo pipeline (simulación de fluido, matriz de Bayer 4x4, atlas de caracteres,
   distorsión por puntero). Se degrada en silencio si no hay WebGL2. */
(function(){
"use strict";
var canvas = document.getElementById('dither');
if (!canvas) return;
var motion = window.matchMedia('(prefers-reduced-motion: reduce)');

var FC = 80, FR = 60, FN = FC * FR;
var CC = 60, EDGE_LO = 36, EDGE_HI = 130;
var EDGES = ['.', ',', '=', '+', '-'];
var BRIGHTS = ['A','S','O','B','A','R','E','S'];
var ALL_CHARS = EDGES.concat(BRIGHTS);
var BAYER = [0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5];
var TL = 320, TS = 10, TM = 72;
var TRAIL_CFG = { fb: 0.08, fss: 18, ffm: 0.15, fir: 0.8, firl: 1.0 };

var VS = '#version 300 es\nin vec2 a_pos;\nvoid main(){ gl_Position = vec4(a_pos, 0, 1); }';

var FS = '#version 300 es\n' +
'precision highp float;\n' +
'uniform sampler2D uFluid, uAtlas;\n' +
'uniform vec2 uRes;\n' +
'uniform float uTime;\n' +
'uniform int uPhase, uTrailN;\n' +
'uniform vec4 uTP[' + TM + '];\n' +
'uniform float uTL[' + TM + '];\n' +
'out vec4 O;\n' +
'const float CC = ' + CC + '.0, EL = ' + EDGE_LO + '.0, EH = ' + EDGE_HI + '.0;\n' +
'const float FC = ' + FC + '.0, FR = ' + FR + '.0;\n' +
'const int BAYER[16] = int[16](' + BAYER.map(function(v){return Math.round((v/16)*255);}).join(',') + ');\n' +
'const int CHAR_N = ' + ALL_CHARS.length + ';\n' +
'float signal(vec2 uv){\n' +
'  float horizon = smoothstep(0.0, 0.45, uv.y) * (1.0 - smoothstep(0.55, 1.0, uv.y));\n' +
'  float band = 1.0 - abs(uv.y - 0.5) * 2.0;\n' +
'  float swell = sin(uv.x * 5.2 + uTime * 0.55) * 0.5 + 0.5;\n' +
'  float ripple = sin(uv.y * 7.5 - uTime * 0.42 + uv.x * 3.1) * 0.5 + 0.5;\n' +
'  float pulse = sin((uv.x + uv.y) * 3.4 - uTime * 0.33) * 0.5 + 0.5;\n' +
'  float s = 0.16 + band * 0.26 + horizon * (swell * 0.34 + ripple * 0.22 + pulse * 0.18);\n' +
'  return clamp(s, 0.0, 1.0);\n' +
'}\n' +
'void main(){\n' +
'  float cw = uRes.x / CC;\n' +
'  float rows = ceil(uRes.y / cw) + 1.0;\n' +
'  float gx = floor(gl_FragCoord.x / cw);\n' +
'  float gy = floor((uRes.y - gl_FragCoord.y) / cw);\n' +
'  if(gx >= CC || gy >= rows) discard;\n' +
'  vec2 cp = vec2(fract(gl_FragCoord.x / cw), fract((uRes.y - gl_FragCoord.y) / cw));\n' +
'  vec2 bp = vec2((gx + 0.5) * cw, (gy + 0.5) * cw);\n' +
'  ivec2 fc = ivec2(gx / CC * FC, gy / rows * FR);\n' +
'  fc = clamp(fc, ivec2(0), ivec2(int(FC)-1, int(FR)-1));\n' +
'  vec2 flow = texelFetch(uFluid, fc, 0).rg;\n' +
'  vec2 disp = vec2(0.0);\n' +
'  for(int i = 0; i < uTrailN; i++){\n' +
'    float life = uTL[i];\n' +
'    if(life <= 0.0) continue;\n' +
'    vec2 d = bp - uTP[i].xy;\n' +
'    float dist = length(d);\n' +
'    float r = 5.0 + life * 3.0;\n' +
'    if(dist == 0.0 || dist > r) continue;\n' +
'    float f = pow(1.0 - dist / r, 2.0);\n' +
'    disp += (d / dist) * f * life * 3.0 + uTP[i].zw * f * 0.04;\n' +
'  }\n' +
'  vec2 sp = bp + disp + flow * 6.0;\n' +
'  vec2 uv = clamp(sp / uRes, 0.0, 1.0);\n' +
'  float s = signal(uv);\n' +
'  float bg = smoothstep(0.06, 0.62, s) * 255.0;\n' +
'  float hm = min(1.0, length(flow) * 1.1);\n' +
'  float gray = bg * (1.0 - hm) + (255.0 - bg) * hm;\n' +
'  float thr = float(BAYER[(int(gy) & 3) * 4 + (int(gx) & 3)]);\n' +
'  bool invDark = hm > 0.05 && bg > thr && gray <= thr;\n' +
'  bool lit = gray > thr;\n' +
'  if(!lit && !invDark) discard;\n' +
'  float pg = invDark ? bg : gray;\n' +
'  int ci;\n' +
'  if(pg >= EL && pg <= EH) ci = uPhase % 5;\n' +
'  else if(pg > EH) ci = 5 + uPhase % ' + BRIGHTS.length + ';\n' +
'  else discard;\n' +
'  float au = (float(ci) + cp.x) / float(CHAR_N);\n' +
'  float ca = texture(uAtlas, vec2(au, cp.y)).a;\n' +
'  if(ca < 0.05) discard;\n' +
'  vec3 teal   = vec3(0.059, 0.463, 0.431);\n' +
'  vec3 cyan   = vec3(0.051, 0.580, 0.529);\n' +
'  vec3 deep   = vec3(0.043, 0.369, 0.345);\n' +
'  vec3 green  = vec3(0.102, 0.498, 0.306);\n' +
'  float tint = smoothstep(0.15, 0.9, uv.x * 0.6 + uv.y * 0.4);\n' +
'  vec3 col = mix(teal, cyan, tint);\n' +
'  col = mix(col, deep, hm * 0.65);\n' +
'  col = mix(col, green, smoothstep(0.72, 1.0, uv.x) * 0.45);\n' +
'  float a = (invDark ? 0.85 : 1.0) * ca;\n' +
'  O = vec4(col * a, a);\n' +
'}\n';

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
try { gl = canvas.getContext('webgl2', { alpha: true, antialias: false, premultipliedAlpha: true, preserveDrawingBuffer: true }); } catch (e) { gl = null; }
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
  function resize(){
    var rect = canvas.getBoundingClientRect();
    W = canvas.width = Math.max(1, Math.round(rect.width));
    H = canvas.height = Math.max(1, Math.round(rect.height));
    gl.viewport(0, 0, W, H);
  }
  resize();
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

  var uTP = loc('uTP'), uTLoc = loc('uTL'), uRes = loc('uRes');
  var uPhase = loc('uPhase'), uTrailN = loc('uTrailN'), uTime = loc('uTime');
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
    gl.clearColor(0, 0, 0, 0);
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
