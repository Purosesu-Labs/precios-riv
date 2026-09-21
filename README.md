# precios-riv

Propuesta comercial de precios del agente de WhatsApp con IA para **AsoBares**.

Publicada con GitHub Pages en: https://purosesu-labs.github.io/precios-riv/

## Diseño

Superficie **Compare** (skill `diseno-propuestas-comerciales`): tres modalidades
alineadas con una marcada como RECOMENDADA, tipografía IBM Plex y acento teal
`#0f766e`. La banda superior usa el **Dither Canvas** de
[ObsidianUI](https://www.obsidianui.dev/docs/dither-canvas).

## Modalidades

| | Esencial | Profesional ★ | A la medida |
|---|---|---|---|
| Precio base | $80.000 | $190.000 | A convenir |
| IVA 19% | $15.200 | $36.100 | — |
| **Valor final con IVA** | **$95.200** | **$226.100** | — |
| Mensajes incluidos | 1.000 | 3.000 | Desde 8.000 |
| **Precio por mensaje** | **$80** | **$63** | A convenir |
| Costo de IA al mes | $359 | $1.078 | Al costo real |
| Mensaje extra | $60 | $60 | A convenir |
| Servidor | 1 slice | 8 slices | 16–32 slices |
| Soporte gestionado | No incluido | Incluido | Según acuerdo |
| Margen bruto | 99,0% | 99,2% | A calcular |

El margen se calcula con la infraestructura prorrateada ($480 por negocio). Si un
negocio tuviera que cubrir el servidor completo, el margen de Esencial baja a
84,6%.

## Costos verificados

- **IA — DeepSeek V4.1 Flash** (`deepseek-flash`): $0,15 / M tokens de entrada
  (cache miss off-peak), $0,003 / M (cache hit), $0,60 / M de salida.
  - Modelo de tokens medido sobre el código: prompt base 1.140 + datos 120 +
    herramientas 1.664 + historial + mensaje = **~3.180 tokens de entrada por mensaje**.
  - Conversación normal (6 mensajes, 82 tok de salida medidos): **$2,16 con caché** /
    **$12,05 sin caché**.
  - Plan de 1.000 mensajes: **$359/mes con caché** / **$2.008 sin caché**.
- **Servidor — InterServer**: Cloud VPS desde **US$3/mes** (1 core, 2 GB RAM,
  40 GB SSD); Web Hosting Standard US$7/mes de renovación.
- **WhatsApp — Meta**: los mensajes de servicio son gratuitos dentro de la ventana
  de 24 h. El agente solo responde; nunca envía plantillas de marketing.

## Medición real

Una conversación de WhatsApp real, tokenizada con `tiktoken`
(`contar_tokens_conversacion.py`):

| Métrica | Medido |
|---|---|
| Texto en pantalla | 693 tokens |
| Entrada facturada al LLM | **25.394 tokens (36,6×)** |
| Salida | 506 tokens (82 por respuesta) |
| Costo de la conversación | **$3,26 COP** |

Validación: el modelo predijo ~3.174 tokens de entrada por turno contra 2.924 de
prompt fijo (−7,9% de error). La **salida** estaba subestimada: el modelo asumía
35 tokens y el agente real escribe 82 (2,3×).

Fuentes:
- https://api-docs.deepseek.com/quick_start/pricing
- https://www.interserver.net/vps/
- https://www.interserver.net/webhosting/

## Efecto de fondo

La banda superior usa **Dither Canvas** de ObsidianUI como réplica fiel: superficie
blanca opaca, rejilla de caracteres sobre atlas monoespaciado, matriz de Bayer 4×4
como umbral, simulación de fluido (diffuse → project → advect) y distorsión por
puntero. Lo único que cambia respecto al original es la fuente de la señal: el
proyecto no cuenta con el video, así que se genera proceduralmente con ruido fBm,
domain warping y bandas direccionales. El número de columnas se deriva del ancho,
de modo que el glifo mide igual en la portada y en una columna estrecha. Se degrada
en silencio a un fallback CSS si no hay WebGL2.

El módulo es `dither_js.py` y está parametrizado: `dither_js(TEAL)` en esta página
e `dither_js(INDIGO)` en la documentación interna.

## Generación

El HTML se genera con `build_propuesta.py` (+ `data_precios.py`,
`simulacion_tokens.py`, `simulador_js.py` y `dither_js.py`) del repositorio
`agentes-asobares`. Este repositorio contiene solo el artefacto publicado:
`index.html` y su copia `404.html`.
