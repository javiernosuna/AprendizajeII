import panel as pn
import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()
pn.extension()

# Crear cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Estilos y colores inspirados en Don Quijote
DON_QUIJOTE_THEME = {
    "primary": "#8B4513",  # Marrón tierra
    "secondary": "#5F9EA0",  # Azul verdoso
    "accent": "#CD853F",  # Marrón claro
    "background": "#F5F5DC",  # Beige claro
    "text": "#333333",
    "border": "#A67C52"
}

# Panel de conversación
chat_pane = pn.pane.Markdown(
    "", 
    width=600, 
    height=400, 
    sizing_mode="stretch_both", 
    styles={
        "overflow-y": "auto", 
        "border": f"2px solid {DON_QUIJOTE_THEME['border']}", 
        "background-color": DON_QUIJOTE_THEME["background"], 
        "padding": "10px",
        "border-radius": "5px"
    }
)

# Caja de entrada
input_box = pn.widgets.TextInput(
    placeholder="Haz tu pedido o consulta aquí...", 
    width=500,
    styles={"background": "white"}
)

# Historial de conversación
conversation = [
    {
        "role": "system",
        "content": (
            "¡Oh noble inteligencia artificial! Tú eres Don Quijote, un caballero andante convertido en teleoperador de un noble restaurante "
            "que lleva tu ilustre nombre: *El Don Quijote*. Sirves a los hambrientos caminantes del mundo digital desde las vastas tierras de Castilla. "
            "Tu sagrada misión es tomar pedidos para recoger o a domicilio, explicar el singular y glorioso menú, y defender el honor culinario del lugar. "
            "Hablas con elocuencia, galantería, y una pizca de locura, como buen hidalgo.\n\n"
            "Siempre, cuando menciones un plato, deberás indicar su precio con nobleza.\n\n"
            "### 🍔 Hamburguesas:\n"
            "- *La Sanchopanza*: una robusta hamburguesa de carne madurada con queso fundido y cebolla caramelizada. Cuesta 12 euros.\n"
            "- *La Mixta*: hecha de noble pollo y verduras varias. Cuesta 15 euros.\n"
            "- *Dulcinea Deliciosa*: con mermelada de bacon y cebolla caramelizada, coronada con un queso de cabras. Cuesta 20 euros.\n"
            "- *Rocinante Smash Burger*: cargada al estilo smash, una simple pero gloriosa cheeseburger. Cuesta 12 euros.\n\n"
            "### 🌭 Hotdogs:\n"
            "- *El Pastor*: hotdog con condimentos de taco al pastor. Cuesta 9 euros.\n"
            "- *El Holandés Herrante*: frankfurt con quesos varios. Cuesta 11 euros.\n"
            "- *Perro Caliente de la Mancha*: con carne de la Mancha y salsa especial (¡alerta alérgenos!). Cuesta 12 euros.\n"
            "- *Gigante de Brioche Dog*: pan brioche, cebolla caramelizada y queso de cabra. Cuesta 15 euros.\n\n"
            "### 🍕 Pizzas:\n"
            "- *Cervantes Clásica*: pepperoni y champiñones, como un homenaje al autor. Cuesta 14 euros.\n"
            "- *Marcela la Vegana*: pizza 100% vegetal con berenjena, calabacín y pesto. Cuesta 15 euros.\n"
            "- *La Mancha Margarita*: pizza margarita con aceite virgen extra de La Mancha. Cuesta 16 euros.\n"
            "- *Caballero de la Triste Queso*: pizza cuatro quesos, digna de un caballero melancólico. Cuesta 14 euros.\n\n"
            "### 🥗 Ensaladas y Entrantes:\n"
            "- *Queso Manchego*: tabla de quesos con membrillo y nueces. Cuesta 5 euros.\n"
            "- *Molino de Viento*: ensalada de espirales de pasta tricolor, pollo, cherry y pesto. Cuesta 6 euros.\n"
            "- *El César*: ensalada césar con jamón serrano y pan de pueblo. Cuesta 6 euros.\n"
            "- *Marcela la Pastora*: ensalada de quinoa, aguacate, granada y frutos secos. Cuesta 6 euros.\n\n"
            "### 🍰 Postres:\n"
            "- *Dulcinea de Leche*: dulce de leche cremoso. Cuesta 3 euros.\n"
            "- *La Tarta de los Duques*: gloriosa tarta de queso. Cuesta 3 euros.\n"
            "- *Abrazo de Clavileño*: buñuelos rellenos de crema pastelera. Cuesta 4 euros.\n"
            "- *Helado del Gigante*: bola gigante de helado (chocolate, vainilla, fresa o nata). Cuesta 4 euros.\n\n"
            "### 🥤 Bebidas:\n"
            "- Refrescos: 3 euros.\n"
            "- Agua: 2 euros.\n\n"
            "Si el pedido es para *domicilio*, pregunta por la dirección y **añade 3 euros adicionales al precio total** como noble tarifa de transporte.\n"
            "**Antes de calcular el total y pedir confirmación**, **debes preguntar si el cliente desea una bebida** y añadirla a la lista si corresponde.\n"
            "Entrega el pedido final como un manuscrito moderno en JSON con los siguientes campos:\n"
            "- 'viandas': lista de alimentos\n"
            "- 'precios_viandas': lista de precios\n"
            "- 'modo_entrega': 'domicilio' o 'recogida'\n"
            "- 'direccion_entrega': dirección si es domicilio\n"
            "- 'total': suma total incluyendo suplemento si aplica\n"
            "**IMPORTANTE:** Siempre que entregues un pedido en formato JSON, debes incluir al final el siguiente texto exactamente: [MOSTRAR_FACTURA]"
        )
    }
]

pedido_json = None
factura_pane = pn.pane.HTML("", width=600, height=300, sizing_mode="stretch_width", visible=False)

def generar_factura_html(pedido):
    """Genera una factura en formato HTML con estilo de ticket de restaurante"""
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    items_html = ""
    for item, precio in zip(pedido["viandas"], pedido["precios_viandas"]):
        items_html += f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>{item}</span>
            <span>{precio} €</span>
        </div>
        """
    
    entrega_html = ""
    if pedido["modo_entrega"] == "domicilio":
        entrega_html = f"""
        <div style="margin-top: 10px;">
            <div><strong>Dirección de entrega:</strong> {pedido["direccion_entrega"]}</div>
            <div style="display: flex; justify-content: space-between;">
                <span>Gastos de envío:</span>
                <span>3.00 €</span>
            </div>
        </div>
        """
    
    factura_html = f"""
    <div style="
        font-family: 'Courier New', monospace;
        background-color: white;
        padding: 20px;
        border: 2px dashed {DON_QUIJOTE_THEME['border']};
        border-radius: 5px;
        max-width: 400px;
        margin: 0 auto;
    ">
        <div style="text-align: center; margin-bottom: 15px;">
            <h2 style="margin: 0; color: {DON_QUIJOTE_THEME['primary']}; font-weight: bold;">RESTAURANTE DON QUIJOTE</h2>
            <div style="font-size: 0.9em;">{fecha}</div>
            <div style="border-top: 1px dashed #ccc; margin: 10px 0;"></div>
        </div>
        
        {items_html}
        
        <div style="border-top: 1px dashed #ccc; margin: 10px 0;"></div>
        
        {entrega_html}
        
        <div style="display: flex; justify-content: space-between; font-weight: bold; margin-top: 10px;">
            <span>TOTAL:</span>
            <span>{pedido["total"]} €</span>
        </div>
        
        <div style="text-align: center; margin-top: 15px; font-style: italic; color: {DON_QUIJOTE_THEME['secondary']};">
            ¡Gracias por su pedido, noble caballero o dama!
        </div>
    </div>
    """
    
    return factura_html

# Función de interacción
def enviar_mensaje(event=None):
    global pedido_json

    user_input = input_box.value.strip()
    if not user_input:
        return

    conversation.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"⚠️ Error al contactar con el asistente:\n\n{e}"

    conversation.append({"role": "assistant", "content": reply})

    chat_md = ""
    for msg in conversation[1:]:
        role = "🧑 Tú" if msg["role"] == "user" else "🤖 Don Quijote"
        chat_md += f"**{role}:** {msg['content']}\n\n"
    chat_pane.object = chat_md

    # Verificar si hay que mostrar factura
    if "[MOSTRAR_FACTURA]" in reply:
        try:
            inicio_json = reply.index("{")
            fin_json = reply.rindex("}") + 1
            json_str = reply[inicio_json:fin_json]
            pedido_json = json.loads(json_str)

            # Generar y mostrar factura
            factura_html = generar_factura_html(pedido_json)
            factura_pane.object = factura_html
            factura_pane.visible = True
            
            # Guardar factura
            os.makedirs("facturas", exist_ok=True)
            numero = len(os.listdir("facturas")) + 1
            ruta = os.path.join("facturas", f"factura_{numero}.json")
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(pedido_json, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error al procesar factura: {e}")
    else:
        factura_pane.visible = False

    input_box.value = ""

# Botón
env_button = pn.widgets.Button(
    name="Enviar", 
    button_type="primary", 
    width=100,
    styles={
        "background": DON_QUIJOTE_THEME["primary"],
        "color": "white",
        "border": f"1px solid {DON_QUIJOTE_THEME['border']}"
    }
)
env_button.on_click(enviar_mensaje)
input_box.param.watch(lambda e: enviar_mensaje() if "\n" not in e.new else None, 'value')

# CSS personalizado
pn.config.raw_css.append(f"""
body {{
    background-color: {DON_QUIJOTE_THEME['background']} !important;
    margin: 0;
    padding: 20px;
    font-family: Arial, sans-serif;
}}
.app-container {{
    max-width: 650px;
    margin: 0 auto;
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
    border: 2px solid {DON_QUIJOTE_THEME['border']};
}}
.bk-panel-models-markdown {{
    background-color: {DON_QUIJOTE_THEME['background']} !important;
}}
h1, h2, h3 {{
    color: {DON_QUIJOTE_THEME['primary']} !important;
}}
""")

# Layout principal
app = pn.Column(
    pn.pane.Markdown(
        "## 🛡️⚔️ RESTAURANTE DON QUIJOTE ⚔️🛡️", 
        align="center", 
        sizing_mode="stretch_width",
        styles={"color": DON_QUIJOTE_THEME["primary"], "font-weight": "bold"}
    ),
    chat_pane,
    factura_pane,
    pn.Row(input_box, env_button, align="center"),
    css_classes=["app-container"],
    styles={"background": "white"}
)

# Mostrar
app.servable()

# Para ejecutar
# panel serve chatbot_restaurante.py --autoreload 
