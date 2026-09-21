# -*- coding: utf-8 -*-
"""Cuenta los tokens reales de una conversación de WhatsApp del agente.

Usa tiktoken (cl100k_base) como aproximación al tokenizer de DeepSeek.
DeepSeek usa su propio BPE, pero cl100k es una referencia cercana para
español; el margen típico es ±10%.

Lo importante no es el número exacto de un mensaje, sino reproducir CÓMO
crece el prompt turno a turno: el agente reenvía el historial completo en
cada llamada, así que el costo no es lineal.
"""
import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")

# Mensajes tal como están en el chat, en orden. rol: 'u' usuario, 'a' agente.
# El texto de cada mensaje va EXACTO al chat pegado (sin las marcas de hora).
CONV = [
    ("u", "Hola, buenas noches"),
    ("a", "⚠️ Aviso de privacidad\nAl continuar esta conversación autorizas el tratamiento de tus datos personales (nombre, teléfono y mensajes) para atender tu solicitud, conforme a la Ley 1581 de 2012.\n\nPuedes conocer, actualizar o solicitar la eliminación de tus datos escribiendo a este mismo número. Si no estás de acuerdo, responde NO AUTORIZO y no continuaremos tratando tus datos."),
    ("u", "Autorizo"),
    ("a", "¡Hola! Buenas noches 😊 ¿Cómo estás? Soy el Asistente de la Tienda de Barrio de don Jaime, encantado de atenderte.\n\n¿En qué te puedo colaborar hoy? Ya sea para hacer un pedido, reservar, preguntar por productos o lo que necesites, aquí estoy para ayudarte. Y recuerda que los *martes tenemos 2x1* en varios productos 😉"),
    ("u", "prueba E164"),
    ("u", "Que productos tienes"),
    ("u", "Hola"),
    ("a", "¡Hola! 😊 Con mucho gusto te cuento que tenemos disponible la Bandeja Paisa por *$32,000*. Incluye frijoles, chicharrón, carne y huevo, ¡todo un clásico! ¿Te gustaría ordenarla o prefieres conocer algo más del menú?"),
    ("a", "¡Hola! Con mucho gusto te cuento lo que tenemos disponible hoy 😊\n\n📦 Bandeja Paisa: *$32.000* — Lleva frijoles, chicharrón, carne y huevo. ¡Está disponible!\n\n¿Te gustaría ordenar una, o prefieres que te cuente sobre algo más del menú?"),
    ("u", "Quiero ordenarla"),
    ("a", "¡Claro que sí! 😊 La Bandeja Paisa es una excelente elección.\n\nPara tomar tu pedido necesito unos datos:\n•  📝 Tu *nombre*\n•  📞 Tu *teléfono*\n•  🛵 ¿La quieres para *recoger* en el local o prefieres *domicilio*? (si es domicilio, necesito la dirección)\n\nCon eso te la dejo lista al toque. ¡Y recuerda que los *martes tenemos 2x1*! 😉"),
    ("u", "Miguel Ángel Riveros, mi número es 3196399649"),
    ("a", "¡Perfecto, Miguel Ángel! 😊 Ya tengo tu nombre y teléfono.\n\nSolo me falta un dato: ¿la Bandeja Paisa la quieres para *recoger* en el local o prefieres *domicilio*? Si es domicilio, me pasas la dirección por favor."),
    ("u", "Para recoger"),
    ("a", "¡Hola! Claro que sí 😊 Te cuento que tenemos disponible la Bandeja Paisa por *$32.000*. Incluye frijoles, chicharrón, carne y huevo. ¿Te la preparo para recoger? Solo dime a qué hora pasas y con gusto la dejamos lista. 🙌"),
    ("a", "¡Listo, Laura! Tu pedido quedó registrado. 😊\n\n🧾 Pedido: #3\n📦 2x Bandeja Paisa\n💰 Total: $64.000\n🚚 A domicilio (carrera 45 #12-30)\n\nTe avisamos cuando esté listo."),
]

# Resultado de la herramienta consultar_catalogo que disparó el agente al pedir
# productos. No está en el chat (es interna) pero SÍ consume tokens de entrada.
TOOL_CATALOGO = """📦 *Bandeja Paisa*
  • $32,000 — Frijoles, chicharrón, carne y huevo [✅ Disponible]
📦 *Arepa de huevo*
  • $6,000 — Arepa frita con huevo [✅ Disponible]
📦 *Jugo natural*
  • $5,000 — Jugo de fruta natural [✅ Disponible]"""

# Definición de la herramienta crear_pedido que el agente usa al final.
TOOL_CREAR_PEDIDO = """crear_pedido(negocio_id: int, cliente_nombre: str, cliente_telefono: str, items: list, tipo_entrega: str, direccion: str = "") -> str
Registra un pedido nuevo en el sistema.

Usa esta herramienta cuando el cliente confirme que quiere ordenar productos del catálogo,
una vez tengas su nombre, teléfono y la forma de entrega.

Args:
    negocio_id: ID del negocio.
    cliente_nombre: Nombre del cliente.
    cliente_telefono: Teléfono de contacto.
    items: Lista de productos con cantidad.
    tipo_entrega: "recoger" o "domicilio".
    direccion: Dirección si es domicilio.

Returns:
    String con el resumen del pedido registrado y su número."""


def tok(s: str) -> int:
    return len(ENC.encode(s))


if __name__ == "__main__":
    print("=== TOKENS DE CADA MENSAJE (cl100k_base) ===")
    print(f"{'#':>3} {'rol':>4} {'tokens':>7}  texto")
    print("-" * 78)
    total_u = total_a = 0
    for i, (rol, txt) in enumerate(CONV, 1):
        t = tok(txt)
        if rol == "u":
            total_u += t
        else:
            total_a += t
        preview = txt.replace("\n", " ")[:44]
        print(f"{i:>3} {'user' if rol=='u' else 'bot':>4} {t:>7}  {preview}")

    print("-" * 78)
    print(f"{'':>3} {'':>4} {total_u+total_a:>7}  TOTAL ({total_u} usuario + {total_a} agente)")
    print()
    print("=== CONTENIDO INTERNO (no aparece en el chat pero se paga) ===")
    print(f"  Resultado de consultar_catalogo : {tok(TOOL_CATALOGO):>6} tok")
    print(f"  Esquema de crear_pedido         : {tok(TOOL_CREAR_PEDIDO):>6} tok")
    print()
    hist = [t for _, t in CONV]
    print(f"  Mensajes de la conversación     : {len(CONV)}")
    print(f"  Tokens de texto intercambiado   : {tok(''.join(hist)):>6} tok")
