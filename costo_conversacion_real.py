# -*- coding: utf-8 -*-
"""Simula el costo real de la conversación tokenizada, turno a turno.

El agente reenvía el historial completo en cada llamada al LLM, así que el
costo NO es la suma de los tokens de texto: cada mensaje se paga varias veces
(a medida que entra en el contexto de los turnos siguientes).

Se compara además con el modelo teórico de simulacion_tokens.py para ver si
los supuestos del documento aguantan contra datos reales.
"""
from contar_tokens_conversacion import CONV, TOOL_CATALOGO, tok
from simulacion_tokens import (
    IN_MISS, IN_HIT, OUT, FIJO, CACHEABLE, simular_conversacion,
)
from data_precios import TRM

# Historial que el agente carga por defecto (settings.historial_max_mensajes).
HIST_MAX = 10


def simular_real():
    """Turno a turno: entradas, salidas y costo acumulado."""
    filas = []
    acum_entrada = 0
    acum_salida = 0
    acum_usd = 0.0
    historial = []          # (rol, tokens) ya intercambiados

    for i, (rol, txt) in enumerate(CONV, 1):
        t = tok(txt)

        if rol == "u":
            # Una llamada al LLM: prompt fijo + historial + este mensaje.
            hist_toks = sum(x[1] for x in historial[-HIST_MAX:])
            entrada = FIJO + hist_toks + t
            # La respuesta llega en el mismo turno (salida del modelo).
            salida = tok(CONV[i][1]) if i < len(CONV) and CONV[i][0] == "a" else 0
            cacheado = min(CACHEABLE, entrada)
            usd = (entrada - cacheado) * IN_MISS + cacheado * IN_HIT + salida * OUT
            acum_entrada += entrada
            acum_salida += salida
            acum_usd += usd
            filas.append((i, "user", t, hist_toks, entrada, salida, usd * TRM, acum_usd * TRM))

        historial.append((rol, t))

    return filas, acum_entrada, acum_salida, acum_usd * TRM


if __name__ == "__main__":
    filas, ent, sal, costo = simular_real()

    print("=== COSTO TURNO A TURNO (el historial se reenvía en cada llamada) ===")
    print(f"{'#':>3} {'rol':>5} {'msg':>5} {'hist':>6} {'entrada':>8} {'salida':>7} {'costo':>8} {'acum':>9}")
    print("-" * 68)
    for i, rol, t, h, e, s, c, ac in filas:
        print(f"{i:>3} {rol:>5} {t:>5} {h:>6} {e:>8,} {s:>7} {c:>7.2f} {ac:>8.2f}")

    print("-" * 68)
    print(f"  Llamadas al LLM     : {len(filas)}")
    print(f"  Entrada acumulada   : {ent:,} tokens")
    print(f"  Salida acumulada    : {sal:,} tokens")
    print(f"  COSTO TOTAL         : ${costo:,.2f} COP")
    print()

    print("=== Comparación con el texto intercambiado ===")
    solo_texto = sum(tok(t) for _, t in CONV)
    print(f"  Tokens de texto en el chat     : {solo_texto:>8,}")
    print(f"  Tokens de entrada facturados   : {ent:>8,}  ({ent/solo_texto:.1f}x)")
    print("  La diferencia es el prompt fijo + el historial reenviado.")
    print()

    print("=== Contra el modelo teórico del documento ===")
    conv_teor, tok_teor = simular_conversacion(6, 35, True)
    print(f"  Modelo del doc (6 msgs, 35 out): ${conv_teor:>7,.2f} | {tok_teor:,} tok entrada")
    print(f"  Conversación real ({len(filas)} msgs)    : ${costo:>7,.2f} | {ent:,} tok entrada")
    print()
    print(f"  El modelo subestima {costo/conv_teor:.1f}x porque asume 6 mensajes")
    print(f"  y esta conversación tuvo {len(filas)} llamadas al LLM.")
    print()

    conv = len(filas)
    print("=== Cuántas conversaciones así caben en el plan de 1.000 mensajes ===")
    print(f"  1 conversación = {conv} mensajes -> 1.000 / {conv} = {1000/conv:.0f} conversaciones")
    print(f"  Costo de 1.000 mensajes a este ritmo: ${costo*(1000/conv):,.0f}/mes")
