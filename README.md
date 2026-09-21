# precios-riv

Propuesta comercial de precios del agente de WhatsApp con IA para **AsoBares**.

Diseño: superficies **Compare** (skill `diseno-propuestas-comerciales`) — tres
modalidades alineadas con una marcada como RECOMENDADA, tipografía IBM Plex y
acento teal `#0f766e`. El fondo del título usa **Dither Canvas** de ObsidianUI
adaptado a la paleta teal.

## Modalidades

| | Esencial | Profesional ★ | A la medida |
|---|---|---|---|
| Precio base | $80.000 | $190.000 | A convenir |
| Con IVA | $95.200 | $226.100 | — |
| Mensajes | 1.000 | 3.000 | Desde 8.000 |
| Servidor | 1 slice | 8 slices | 16–32 slices |
| Margen | 84,6% | 99,2% | A calcular |

Publicada con GitHub Pages en: https://purosesu-labs.github.io/precios-riv/

## Contenido

Un solo plan para los afiliados:

| Concepto | Valor |
|---|---|
| Precio base | $80.000 COP / mes |
| IVA 19% | $15.200 COP |
| **Valor final** | **$95.200 COP / mes** |
| Mensajes incluidos | 1.000 / mes |
| Instalación | Gratis |

## Costos verificados

- **IA — DeepSeek V4.1 Flash** (`deepseek-flash`): $0,15 / M tokens de entrada (cache miss off-peak), $0,003 / M (cache hit), $0,60 / M de salida.
  - Modelo de tokens medido sobre el código: prompt base 1.140 + datos 120 + herramientas 1.664 + historial + mensaje = **~3.180 tokens de entrada por mensaje**.
  - Conversación normal (6 mensajes, 82 tok de salida medidos): **$2,16 con caché** / **$12,05 sin caché**.
  - Plan de 1.000 mensajes: **$359/mes con caché** / **$2.008 sin caché**.

## Medición real

Una conversación de WhatsApp real, tokenizada con `tiktoken` (`contar_tokens_conversacion.py`):

| Métrica | Medido |
|---|---|
| Texto en pantalla | 693 tokens |
| Entrada facturada al LLM | **25.394 tokens (36,6×)** |
| Salida | 506 tokens (82 por respuesta) |
| Costo de la conversación | **$3,26 COP** |

Validación: el modelo predijo ~3.174 tokens de entrada por turno contra 2.924 de prompt fijo (−7,9% de error).
La **salida** estaba subestimada: el modelo asumía 35 tokens y el agente real escribe 82 (2,3×).
- **Servidor — InterServer**: Cloud VPS desde **US$3/mes** (1 core, 2 GB RAM, 40 GB SSD); Web Hosting Standard US$7/mes de renovación.

Fuentes:
- https://api-docs.deepseek.com/quick_start/pricing
- https://www.interserver.net/vps/
- https://www.interserver.net/webhosting/

## Margen

Con el precio base de $80.000 COP y el VPS compartido, el margen bruto es del **84,3%** por negocio. El costo de IA representa el 1,1% del precio.

## Generación

El HTML se genera con `build_precios.py` + `data_precios.py` del repositorio `agentes-asobares`. Este repositorio contiene solo el artefacto publicado.

## Efecto de fondo

La banda superior usa **Dither Canvas** de [ObsidianUI](https://www.obsidianui.dev/docs/dither-canvas), adaptado a señal procedural (sin video) conservando la simulación de fluido, la matriz de Bayer 4×4, el atlas de caracteres y la distorsión por puntero. Se degrada a un fallback CSS si no hay WebGL2.
