# -*- coding: utf-8 -*-
"""JS del simulador de precios, inyectado en la página.

Separado de build_precios.py para que las llaves de JavaScript no colisionen
con las del f-string que arma el HTML. Las constantes del modelo llegan desde
data_precios.py (SIM) para que el resultado del simulador no pueda divergir
de las tablas publicadas en el documento.
"""
import json
from data_precios import SIM
from simulacion_tokens import FIJO, CACHEABLE

_CONST = json.dumps({
    k: SIM[k] for k in (
        "trm", "iva", "precio_base", "mensajes_incluidos",
        "in_miss", "in_hit", "out", "precio_excedente",
    )
} | {
    # Modelo de tokens medido (simulacion_tokens.py).
    "fijo": FIJO,              # prompt + datos + herramientas, en cada llamada
    "cacheable": CACHEABLE,    # prefijo estable que DeepSeek puede cachear
    "hist_tok": 30,            # tokens por mensaje previo del historial
    "hist_max": 10,            # historial_max_mensajes por defecto
    "user_tok": 20,            # mensaje del cliente
    "out_msg": 35,             # salida por mensaje en una conversación normal
    "msgs_conv": 6,            # mensajes por conversación (supuesto del doc)
}, ensure_ascii=False)

SIM_JS = r"""
/* Simulador de precios. Las constantes llegan desde data_precios.py para que
   el resultado no pueda divergir de las tablas del documento. */
(function(){
"use strict";
var C = __CONST__;

var elMsgs  = document.getElementById('sim-msgs');
var elNeg   = document.getElementById('sim-negocios');
var elInfra = document.getElementById('sim-infra');
if(!elMsgs || !elNeg || !elInfra) return;

var msgs = +elMsgs.value;
var negocios = +elNeg.value;
var infraCosto = +elInfra.options[elInfra.selectedIndex].dataset.costo;
var infraCap = +elInfra.value;
var usaCache = true;

function cop(n){ return '$' + Math.round(n).toLocaleString('es-CO'); }
function num(n){ return n.toLocaleString('es-CO'); }
function pct(n){ return n.toFixed(1).replace('.', ',') + '%'; }

/* Costo de IA con el modelo medido: prompt fijo (2.924 tok, del que 2.804 es
   prefijo cacheable) + historial que crece + mensaje del cliente.
   El historial se reconstruye segun la posicion del mensaje dentro de la
   conversacion, porque no cuesta lo mismo el 1o que el 6o. */
function costoIA(m, cache){
  if(cache === undefined) cache = true;
  var conv = Math.max(1, C.msgs_conv);
  var completas = Math.floor(m / conv);
  var sobrantes = m % conv;
  var usd = 0;

  function msg(pos){
    var hist = Math.min(pos, C.hist_max) * C.hist_tok;
    var entrada = C.fijo + hist + C.user_tok;
    var cacheado = cache ? Math.min(C.cacheable, entrada) : 0;
    return (entrada - cacheado) * C.in_miss + cacheado * C.in_hit + C.out_msg * C.out;
  }
  var i;
  for(i = 0; i < conv; i++) usd += msg(i) * completas;
  for(i = 0; i < sobrantes; i++) usd += msg(i);
  return usd * C.trm;
}

function calcular(){
  var ia = costoIA(msgs, usaCache);
  var infra = infraCosto / Math.max(1, negocios);
  var costo = ia + infra;

  var excedente = Math.max(0, msgs - C.mensajes_incluidos);
  var cargo = excedente * C.precio_excedente;

  var base = C.precio_base + cargo;
  var iva = base * C.iva;
  var factura = base + iva;

  var margen = base - costo;
  var mPct = base > 0 ? margen / base * 100 : 0;

  document.getElementById('sim-msgs-out').textContent = num(msgs);
  document.getElementById('sim-negocios-out').textContent = num(negocios);
  document.getElementById('sim-incluidos').textContent = num(C.mensajes_incluidos);
  document.getElementById('sim-excedente').textContent = num(excedente);
  document.getElementById('sim-cargo').textContent = cop(cargo);
  document.getElementById('sim-ia').textContent = cop(ia);
  document.getElementById('sim-sup').textContent = usaCache ? 'con caché' : 'sin caché';
  document.getElementById('sim-infra-costo').textContent = cop(infra);
  document.getElementById('sim-costo').textContent = cop(costo);
  document.getElementById('sim-margen').textContent = cop(margen);
  document.getElementById('sim-margen-pct').textContent = pct(mPct);
  document.getElementById('sim-factura').textContent = cop(factura);
  document.getElementById('sim-factura-sub').textContent =
    'Base ' + cop(base) + ' + IVA ' + cop(iva) + (cargo > 0 ? ' (incluye excedente)' : '');

  /* Barra: porcion del precio base consumida por costos. */
  var usado = base > 0 ? Math.min(100, costo / base * 100) : 0;
  document.getElementById('sim-bar-fill').style.width = usado.toFixed(2) + '%';
  document.getElementById('sim-leg-margen').textContent = pct(mPct);
  document.getElementById('sim-leg-ia').textContent = pct(base > 0 ? ia / base * 100 : 0);
  document.getElementById('sim-leg-infra').textContent = pct(base > 0 ? infra / base * 100 : 0);

  /* Aviso de capacidad del servidor. */
  var hint = document.getElementById('sim-capacidad');
  var aviso = document.getElementById('sim-aviso');
  if(negocios > infraCap){
    hint.classList.add('over');
    hint.textContent = 'Capacidad de este servidor: ' + num(infraCap) +
      ' negocios — te pasaste por ' + num(negocios - infraCap);
    aviso.hidden = false;
    document.getElementById('sim-aviso-txt').textContent =
      'Con ' + num(negocios) + ' negocios en un servidor de ' + num(infraCap) +
      ' de capacidad, la talla se queda corta. Sube de slices o reparte los negocios en dos servidores.';
  } else {
    hint.classList.remove('over');
    hint.textContent = 'Capacidad de este servidor: ' + num(infraCap) + ' negocios';
    aviso.hidden = true;
  }

  var botones = document.querySelectorAll('.sim-preset');
  for(var i = 0; i < botones.length; i++){
    botones[i].classList.toggle('on', +botones[i].dataset.msgs === msgs);
  }
}

elMsgs.addEventListener('input', function(){ msgs = +elMsgs.value; calcular(); });
elNeg.addEventListener('input', function(){ negocios = +elNeg.value; calcular(); });
elInfra.addEventListener('change', function(){
  infraCosto = +elInfra.options[elInfra.selectedIndex].dataset.costo;
  infraCap = +elInfra.value;
  elNeg.max = Math.max(infraCap, 1);
  /* Al cambiar de talla, el numero de negocios debe seguir teniendo sentido:
     un servidor de 200 cupos no se compra para 25 negocios. Se ajusta al
     rango razonable de esa talla, respetando lo que el usuario ya eligio
     si cabe. */
  var minRazonable = Math.max(1, Math.round(infraCap * 0.5));
  if(negocios > infraCap || negocios < minRazonable) negocios = minRazonable;
  elNeg.value = negocios;
  calcular();
});

var btnOn = document.getElementById('sim-cache-on');
var btnOff = document.getElementById('sim-cache-off');
var cacheHint = document.getElementById('sim-cache-hint');
function setCache(v){
  usaCache = v;
  btnOn.classList.toggle('on', v);
  btnOff.classList.toggle('on', !v);
  cacheHint.textContent = v
    ? 'El prefijo de 2.804 tokens se reutiliza: es el mejor caso.'
    : 'Si el prefijo no se reutiliza, cada turno paga la entrada completa.';
  cacheHint.classList.toggle('over', !v);
  calcular();
}
btnOn.addEventListener('click', function(){ setCache(true); });
btnOff.addEventListener('click', function(){ setCache(false); });

var presets = document.querySelectorAll('.sim-preset');
for(var j = 0; j < presets.length; j++){
  presets[j].addEventListener('click', function(){
    msgs = +this.dataset.msgs;
    elMsgs.value = msgs;
    calcular();
  });
}

calcular();
})();
""".replace("__CONST__", _CONST)
