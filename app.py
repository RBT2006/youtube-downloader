from flask import Flask, render_template, request, jsonify
import os
import uuid
import base64
import qrcode
from io import BytesIO

app = Flask(__name__, template_folder='templates', static_folder='static')

# Herramientas disponibles
TOOLS = {
    "qr": "Generador de QR",
    "password": "Generador de Contraseñas",
    "base64": "Codificador Base64",
    "text": "Convertidor de Texto",
    "color": "Selector de Colores"
}

@app.route('/')
def index():
    return render_template('index.html')

# ==================== QR CODE ====================
@app.route('/api/qr', methods=['POST'])
def generate_qr():
    data = request.json.get('text', '')
    if not data:
        return jsonify({"error": "Ingresa texto o enlace"}), 400
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({"image": f"data:image/png;base64,{img_str}"})

# ==================== PASSWORD ====================
@app.route('/api/password', methods=['POST'])
def generate_password():
    import random
    import string
    
    length = int(request.json.get('length', 16))
    use_numbers = request.json.get('numbers', True)
    use_symbols = request.json.get('symbols', True)
    
    characters = string.ascii_letters
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    password = ''.join(random.choice(characters) for _ in range(length))
    return jsonify({"password": password})

# ==================== BASE64 ====================
@app.route('/api/base64', methods=['POST'])
def base64_convert():
    text = request.json.get('text', '')
    action = request.json.get('action', 'encode')
    
    try:
        if action == 'encode':
            result = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        else:
            result = base64.b64decode(text).decode('utf-8')
        return jsonify({"result": result})
    except:
        return jsonify({"error": "Error en la conversión"}), 400

@app.route('/api/text', methods=['POST'])
def text_convert():
    text = request.json.get('text', '')
    action = request.json.get('action', 'upper')
    
    if action == 'upper':
        result = text.upper()
    elif action == 'lower':
        result = text.lower()
    elif action == 'capitalize':
        result = text.capitalize()
    else:
        result = text
    return jsonify({"result": result})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
