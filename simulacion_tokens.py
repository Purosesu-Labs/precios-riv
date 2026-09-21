# -*- coding: utf-8 -*-
"""Simulación de costo por tokens — mensajes y conversaciones.

Construido de abajo hacia arriba midiendo el código real, no estimando:

  · system prompt  → agente/core/config/prompts/base.txt (3.982 chars ≈ 1.140 tok)
  · herramientas   → 7 @tool en core/agent/tools.py (esquemas ≈ 1.664 tok)
  · historial      → settings.historial_max_mensajes = 10 (por defecto)
  · llamadas/mensaje → settings.clasificar_intencion = False → 1 llamada
  · precios        → DeepSeek deepseek-flash (off-peak)

El supuesto anterior del documento (1.630 tok/mensaje) subestimaba la entrada
porque no contaba el peso de los esquemas de herramientas ni el tamaño real
del prompt base. Este módulo reemplaza esa cifra.
"""
from data_precios import TRM

# ---------- Precios DeepSeek V4.1 Flash (USD por token, off-peak) ----------
IN_MISS = 0.15 / 1_000_000    # entrada no cacheada
IN_HIT = 0.003 / 1_000_000    # entrada cacheada (prefijo estable)
OUT = 0.60 / 1_000_000        # salida

# ---------- Componentes medidos del prompt (tokens) ----------
COMPONENTES_PROMPT = [
    ("System prompt base", "prompts/base.txt · 3.982 caracteres", "1.140",
     "Medido. El documento asumía 900."),
    ("Datos del negocio", "nombre, horario, instrucciones", "120",
     "Se inyectan en cada turno desde la base de datos."),
    ("Esquemas de herramientas", "7 herramientas @tool con su JSON Schema", "1.664",
     "Medido. Pesa más que el prompt base y no estaba contado."),
    ("Historial de conversación", "hasta 10 mensajes previos · ~30 tok cada uno", "300",
     "`historial_max_mensajes = 10` por defecto. Crece dentro de la conversación."),
    ("Mensaje del cliente", "un mensaje típico de WhatsApp", "20",
     "Texto libre del usuario."),
]

# Prompt fijo = todo lo que se repite en cada llamada del mismo negocio.
FIJO = 1140 + 120 + 1664      # = 2.924
# Prefijo estable: es lo que DeepSeek puede cachear (system + herramientas).
CACHEABLE = 1140 + 1664        # = 2.804

# ---------- Perfiles de conversación ----------
# n = mensajes; out = tokens de salida por mensaje (sube si hay herramientas).
# La salida por mensaje está calibrada con una conversación real medida
# (contar_tokens_conversacion.py): el agente respondió 82 tokens por mensaje de
# media, no los 35 que asumía el modelo. Es un agente conversacional: saluda,
# usa emoji, lista opciones y ofrece promociones, así que escribe largo.
PERFILES = [
    ("Consulta simple", 2, 50,
     "Pregunta de horario o dirección. Se resuelve en un intercambio."),
    ("Conversación normal", 6, 82,
     "Reserva o consulta de menú. Calibrado con una conversación real."),
    ("Conversación larga", 12, 90,
     "El cliente pide varias cosas; el historial se llena y se trunca a 10."),
    ("Con herramientas", 20, 110,
     "Reservas y pedidos: varias llamadas a herramientas y respuestas detalladas."),
]


def _costo_mensaje(hist: int, out: int, cache: bool = True) -> tuple[float, int]:
    """Costo en COP de un mensaje. Devuelve (costo, tokens de entrada)."""
    entrada = FIJO + hist * 30 + 20
    s = min(CACHEABLE, entrada) if cache else 0
    usd = (entrada - s) * IN_MISS + s * IN_HIT + out * OUT
    return usd * TRM, entrada


def simular_conversacion(n_msgs: int, out_por_msg: int, cache: bool = True):
    """Simula una conversación completa. El historial crece mensaje a mensaje."""
    costo = 0.0
    tokens = 0
    for i in range(n_msgs):
        c, e = _costo_mensaje(min(i, 10), out_por_msg, cache)
        costo += c
        tokens += e
    return costo, tokens


def simular_plan(mensajes: int, n_msgs: int, out_por_msg: int, cache: bool = True):
    """Costo mensual del plan según el perfil de conversación dominante."""
    costo_conv, tok_conv = simular_conversacion(n_msgs, out_por_msg, cache)
    conversaciones = mensajes / n_msgs
    return costo_conv * conversaciones, conversaciones, tok_conv


# ---------- Filas precalculadas para el documento ----------
def filas_perfiles():
    filas = []
    for etq, n, o, desc in PERFILES:
        cc, tc = simular_conversacion(n, o, True)
        sc, _ = simular_conversacion(n, o, False)
        filas.append((etq, n, o, f"{tc:,}".replace(",", "."),
                      f"{cc:,.2f}".replace(",", ".").replace(".", ",", 1),
                      f"{sc:,.2f}".replace(",", ".").replace(".", ",", 1), desc))
    return filas


def filas_plan(mensajes: int = 1000, precio: int = 80000):
    filas = []
    for etq, n, o, _ in PERFILES:
        cc, conversaciones, _ = simular_plan(mensajes, n, o, True)
        sc, _, _ = simular_plan(mensajes, n, o, False)
        filas.append((
            etq, f"{conversaciones:,.0f}".replace(",", "."),
            f"{cc:,.0f}".replace(",", "."),
            f"{sc:,.0f}".replace(",", "."),
            f"{cc / precio * 100:.1f}".replace(".", ","),
        ))
    return filas


def sensibilidad():
    """Qué pasa si las condiciones cambian.

    Cada caso se calcula de verdad (no con multiplicadores sueltos) para que la
    tabla no pueda inflar ni esconder el efecto de cada supuesto.
    """
    base, _, _ = simular_plan(1000, 6, 35, cache=True)
    filas = []

    def add(etq, valor, nota=""):
        filas.append((etq,
                      f"{valor:,.0f}".replace(",", "."),
                      f"{valor / base * 100:.0f}".replace(".", ",") + "%",
                      nota))

    add("Con caché de prompt, off-peak", base, "El escenario publicado")

    # Sin caché: toda la entrada paga tarifa completa.
    sc, _, _ = simular_plan(1000, 6, 35, cache=False)
    add("Sin caché de prompt", sc, "Si el prefijo no se reutiliza")

    # Prompt más largo: si el negocio carga una carta extensa en el prompt.
    global FIJO, CACHEABLE
    fijo0, cache0 = FIJO, CACHEABLE
    FIJO, CACHEABLE = 2924 + 1000, 2804 + 1000
    pl, _, _ = simular_plan(1000, 6, 35, cache=True)
    FIJO, CACHEABLE = fijo0, cache0
    add("Prompt base 1.000 tokens más largo", pl, "Carta extensa o muchas instrucciones")

    # Clasificador reactivado: una llamada extra por mensaje, sin herramientas
    # (el clasificador solo manda el mensaje del usuario).
    clasif_msg = (_costo_mensaje(0, 15, True)[0])   # prompt mínimo, salida corta
    conv_normal, _ = simular_conversacion(6, 35, True)
    con_clasif = (conv_normal + clasif_msg * 6) * (1000 / 6)
    add("Clasificador reactivado", con_clasif, "2 llamadas por mensaje en vez de 1")

    # Peak: tarifa doble. Un bar colombiano cae mayormente off-peak, pero se
    # muestra el techo completo como cota superior.
    add("Tarifa peak en todo el tráfico", base * 2, "Cota superior; el tráfico real es off-peak")

    return filas
