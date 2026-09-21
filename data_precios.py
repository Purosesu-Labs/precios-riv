# -*- coding: utf-8 -*-
"""Datos de la página de precios del agente de AsoBares.

Todas las cifras provienen de:
  · analisis/03-costos-y-capacidad.md   (tokens medidos, escenarios de tráfico)
  · MODELO-DE-NEGOCIO.md                (estructura de cobro, márgenes)
  · Precios reales verificados en interserver.net (web hosting y VPS)
  · Precios oficiales de DeepSeek (deepseek-flash, api-docs.deepseek.com)
"""

# ---------- Constantes económicas ----------
TRM = 4000            # COP por USD
IVA = 0.19

PRECIO_BASE = 80000
PRECIO_IVA = int(PRECIO_BASE * IVA)          # 15.200
PRECIO_FINAL = PRECIO_BASE + PRECIO_IVA      # 95.200
MENSAJES_INCLUIDOS = 1000

# ---------- DeepSeek V4.1 Flash (deepseek-flash) ----------
# Precios oficiales por 1M tokens. Off-peak = mitad de peak.
DS = [
    ("Entrada — cache miss", "off-peak", "$0,15", "$0,30"),
    ("Entrada — cache hit", "off-peak", "$0,003", "$0,006"),
    ("Salida", "off-peak", "$0,60", "$1,20"),
]

# ---------- InterServer: precios reales verificados ----------
INTERSERVER = [
    ("Web Hosting Standard", "Renovación mensual", "$7,00", "28.000",
     "Hosting compartido, DirectAdmin, correo y CDN incluidos"),
    ("Cloud VPS · 1 slice", "1 core · 2 GB RAM · 40 GB SSD · 2 TB", "$3,00", "12.000",
     "KVM, IP pública, acceso root, RAID-10 SSD"),
    ("Cloud VPS · 2 slices", "2 cores · 4 GB RAM · 80 GB SSD · 4 TB", "$6,00", "24.000",
     "Punto medio para varios negocios con holgura"),
    ("Cloud VPS · 4 slices", "2 cores · 8 GB RAM · 160 GB SSD · 8 TB", "$12,00", "48.000",
     "Dimensionado para 20–25 negocios según el análisis"),
    ("Cloud VPS · 8 slices", "4 cores · 16 GB RAM · 320 GB SSD · 16 TB", "$24,00", "96.000",
     "Incluye soporte gestionado de InterServer"),
]

# ---------- Costo de IA para 1.000 mensajes ----------
# Medición real del proyecto: ~1.630 tokens entrada + 35 salida por turno.
# El system prompt (~900 tok) es idéntico en cada llamada → cacheable.
COSTO_IA = [
    ("Con caché de prompt", "18.114", "210", "US$ 0,0617", "247".replace(",", ".")),
    ("Sin caché de prompt", "18.114", "210", "US$ 0,4740", "1,895".replace(",", ".")),
]

# ---------- P&L por negocio ----------
# Se compara el costo total del plan contra distintos supuestos de servidor.
PYL = [
    ("VPS 1 slice (compartido entre negocios)", "12.000", "247".replace(",", "."), "12.247", "67.753", "84,7%"),
    ("Web Hosting Standard (instancia dedicada)", "28.000", "247".replace(",", "."), "28.247", "51.753", "64,7%"),
    ("VPS 4 slices (instancia dedicada)", "48.000", "247".replace(",", "."), "48.247", "31.753", "39,7%"),
]

# ---------- Escenarios de consumo ----------
ESCENARIOS = [
    ("Consultas simples", "700", "1.140.000", "24.500", "744", "0,7%"),
    ("Plan contratado", "1.000", "1.630.000", "35.000", "1.062", "1,1%"),
    ("Uso intenso", "2.000", "3.260.000", "70.000", "2.124", "2,2%"),
]

# ---------- Qué incluye el plan ----------
INCLUYE = [
    ("Instalación y alta", "Gratis",
     "Configuración inicial, carga de la carta y puesta en marcha. Sin costo de implementación."),
    ("Mensajes con IA", "1.000 / mes",
     "Cada mensaje que el agente responde. Un cliente que escribe 10 veces seguidas consume 10."),
    ("Negocio", "1",
     "Un establecimiento por plan. Una sede adicional es un plan aparte."),
    ("Usuarios del panel", "Ilimitados",
     "Todo el equipo del bar puede consultar conversaciones, reservas y escaladas."),
    ("Mensajería de WhatsApp", "Sin costo",
     "El agente solo responde dentro de la ventana de servicio de 24 h de Meta. Nunca envía plantillas de marketing."),
    ("Módulos", "Reservas y pedidos",
     "Toma de reservas de mesa y de pedidos contra el menú y los precios reales del negocio."),
    ("Escalado a humano", "Incluido",
     "Cuando el caso lo amerita, avisa al equipo con el historial completo de la conversación."),
    ("Servidor y operación", "Incluido",
     "Infraestructura, dominio, TLS, respaldos diarios, monitoreo y soporte durante el horario hábil."),
    ("Permanencia mínima", "Ninguna",
     "El servicio es mes a mes. Se cancela cuando el negocio quiera, sin penalidad."),
]

# ---------- Fuentes ----------
FUENTES = [
    ("Precios de DeepSeek API", "deepseek-flash (DeepSeek-V4.1-Flash)",
     "https://api-docs.deepseek.com/quick_start/pricing"),
    ("Precios de InterServer — VPS", "Cloud Compute, slices 1 a 32",
     "https://www.interserver.net/vps/"),
    ("Precios de InterServer — Web Hosting", "Standard Web Hosting, renovación mensual",
     "https://www.interserver.net/webhosting/"),
]

# ---------- Flujo de cálculo ----------
FLUJO = [
    ("Se mide el consumo real", "El agente registra tokens de entrada y salida por mensaje en la tabla consumo_negocio (migración 004)."),
    ("Se convierte a dólares", "Los precios de DeepSeek están en USD por millón de tokens; se aplica la TRM de $4.000 COP/USD."),
    ("Se aplica el descuento por caché", "El system prompt es idéntico en cada llamada del mismo negocio, así que entra a precio de cache hit ($0,003/M)."),
    ("Se suma la infraestructura", "El costo del servidor de InterServer se prorratea entre los negocios que aloja."),
    ("Se compara contra el precio", "El precio base de $80.000 menos el costo total da el margen bruto del plan."),
]

# ---------- Arquitectura: centralizado ----------
CENTRALIZADO = [
    ("Qué se instala", "Una copia por bar", "Una sola instalación que atiende a todos"),
    ("Consumo de RAM", "25 copias → 7,0 GB, al límite", "1 copia → 1,5 GB, con 5× de margen"),
    ("Actualizar el agente", "25 despliegues", "1 despliegue"),
    ("Si un bar crece", "Solo le afecta a él, sin cupo", "Se regula por cupo del plan"),
    ("Aislamiento de datos", "Físico: una caja por bar", "Lógico: Row Level Security de PostgreSQL"),
    ("Costo de servidor", "25 servidores", "1 servidor compartido"),
]

# ---------- Slices de InterServer y capacidad ----------
# Recursos publicados por InterServer + consumo medido del stack centralizado.
SLICES = [
    ("1 slice", "1", "2", "40", "3,00", "12.000", "50", "Piloto y primeros afiliados"),
    ("2 slices", "2", "4", "80", "6,00", "24.000", "100", "Crecimiento inicial cómodo"),
    ("4 slices", "2", "8", "160", "12,00", "48.000", "100", "El análisis original pedía esta talla"),
    ("8 slices", "4", "16", "320", "24,00", "96.000", "200", "Incluye soporte gestionado"),
    ("16 slices", "8", "32", "640", "48,00", "192.000", "400", "Varios capítulos regionales"),
    ("32 slices", "16", "64", "1.280", "96,00", "384.000", "800", "Escala nacional"),
]

# ---------- Consumo por componente del stack centralizado ----------
COMPONENTES = [
    ("api · FastAPI + LangGraph", "1 contenedor", "250 MB", "500 MB", "Bajo — limitado por red, no por CPU"),
    ("postgres · datos de los negocios", "25 negocios", "150 MB", "400 MB", "Bajo"),
    ("redis · caché y pub/sub", "1 instancia", "30 MB", "100 MB", "Muy bajo"),
    ("SPA · archivos estáticos", "Nginx", "15 MB", "30 MB", "Muy bajo"),
    ("Sistema operativo + Docker", "—", "500 MB", "500 MB", "—"),
]

# ---------- Cuello de botella ----------
CUELLO = [
    ("1 vCPU sostenida", "1 worker async puede atender decenas de mensajes por segundo"),
    ("50 negocios en pico", "≈ 0,58 mensajes/segundo — el 12% de lo que aguanta un worker"),
    ("100 negocios en pico", "≈ 1,17 mensajes/segundo — el 23%"),
    ("200 negocios en pico", "≈ 2,33 mensajes/segundo — el 47%"),
]

# ---------- Simulador de precios ----------
# Constantes del modelo. Deben coincidir con la tabla de costo de IA publicada:
# a 1.000 mensajes el simulador debe dar $533 COP, igual que la sección 03.
SIM = {
    "trm": TRM,
    "iva": IVA,
    "precio_base": PRECIO_BASE,
    "mensajes_incluidos": MENSAJES_INCLUIDOS,
    # DeepSeek V4.1 Flash, USD por token (off-peak)
    "in_miss": 0.15 / 1_000_000,
    "in_hit": 0.003 / 1_000_000,
    "out": 0.60 / 1_000_000,
    # Medición real del proyecto
    "sys_tok": 900,        # system prompt, idéntico por negocio → cacheable
    "msg_in": 1630,        # tokens de entrada por mensaje
    "msg_out": 35,         # tokens de salida por mensaje
    # Excedente: se cobra por mensaje por encima del tope
    "precio_excedente": 60,
    # Pool de infraestructura: talla del servidor y su costo
    "infra": [
        # (etiqueta, costo COP/mes, capacidad en negocios)
        ("1 slice · 1 core, 2 GB", 12000, 50),
        ("2 slices · 2 cores, 4 GB", 24000, 100),
        ("8 slices · 4 cores, 16 GB", 96000, 200),
        ("16 slices · 8 cores, 32 GB", 192000, 400),
    ],
}

# Presets del simulador: perfiles de bar reconocibles
SIM_PRESETS = [
    ("Bar tranquilo", 400, "Consultas de horario y menú entre semana"),
    ("Bar activo", 1000, "El plan contratado: reservas y pedidos todos los días"),
    ("Bar de noche", 2500, "Alta rotación, eventos y fines de semana cargados"),
    ("Gastrobar de eventos", 5000, "Temporada de eventos privados y campañas"),
]

# Qué muestra cada fila del resultado del simulador
SIM_SALIDAS = [
    ("factura", "Lo que paga el negocio ese mes"),
    ("ia", "Costo real del consumo de IA (interno)"),
    ("infra", "Parte proporcional del servidor (interno)"),
    ("margen", "Lo que queda después de cubrir los costos"),
]

