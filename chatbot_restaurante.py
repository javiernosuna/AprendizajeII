import panel as pn
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()
pn.extension()

# Crear cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Panel de conversación
chat_pane = pn.pane.Markdown(
    "", 
    width=600, 
    height=400, 
    sizing_mode="stretch_both", 
    styles={"overflow-y": "auto", "border": "2px solid #ccc", "background-color": "#ffffff", "padding": "10px"}
)

# Caja de entrada
input_box = pn.widgets.TextInput(placeholder="Haz tu pedido o consulta aquí...", width=500)

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
        )
    }
]

pedido_json = None

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

    # Si contiene JSON, extraerlo y guardarlo
    try:
        inicio_json = reply.index("{")
        fin_json = reply.rindex("}") + 1
        json_str = reply[inicio_json:fin_json]
        pedido_json = json.loads(json_str)

        os.makedirs("facturas", exist_ok=True)
        numero = len(os.listdir("facturas")) + 1
        ruta = os.path.join("facturas", f"factura_{numero}.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(pedido_json, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

    input_box.value = ""

# Botón
env_button = pn.widgets.Button(name="Enviar", button_type="primary", width=100)
env_button.on_click(enviar_mensaje)
input_box.param.watch(lambda e: enviar_mensaje() if "\n" not in e.new else None, 'value')

# CSS personalizado
pn.config.raw_css.append("""
body {
    background-color: transparent !important;
    margin: 0;
    padding: 0;
}
#app-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
}
""")

# Layout principal
app = pn.Column(
    pn.pane.Markdown("## 🛡️⚔️ RESTAURANTE DON QUIJOTE ⚔️🛡️", align="center", sizing_mode="stretch_width"),
    chat_pane,
    pn.Row(input_box, env_button, align="center"),
    css_classes=["app-container"],
    width=650
)
app.css_classes = ["app-container"]

# Mostrar
app.servable()