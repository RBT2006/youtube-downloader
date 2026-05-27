from flask import Flask, request, jsonify, render_template
import os
import uuid
import random
import string
import base64
import qrcode
from io import BytesIO

app = Flask(__name__, template_folder='templates', static_folder='static')

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ==================== RUTA PRINCIPAL ====================
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

# ==================== GENERADOR DE CONTRASEÑAS ====================
@app.route('/api/password', methods=['POST'])
def generate_password():
    length = int(request.json.get('length', 16))
    
    characters = string.ascii_letters + string.digits
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
            result = base64.b64decode(text.encode('utf-8')).decode('utf-8')
        return jsonify({"result": result})
    except:
        return jsonify({"error": "Error en la conversión"}), 400

# ==================== NUEVAS HERRAMIENTAS ====================

# Contador de palabras (no necesita backend, pero lo dejamos por si acaso)
@app.route('/api/wordcount', methods=['POST'])
def word_count():
    text = request.json.get('text', '')
    words = len(text.split())
    chars = len(text)
    return jsonify({"words": words, "characters": chars})

# Generador de Nombres
@app.route('/api/randomname', methods=['GET'])
def random_name():
    first_names = ["Lucas", "Sofía", "Mateo", "Valentina", "Diego", "Camila", "Alejandro", "Isabella", "Martín", "Emma", "Nicolás", "Olivia"]
    last_names = ["García", "Rodríguez", "López", "Martínez", "González", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores"]
    
    full_name = random.choice(first_names) + " " + random.choice(last_names)
    return jsonify({"name": full_name})

# ==================== INICIO ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
