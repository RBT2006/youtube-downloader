from flask import Flask, request, jsonify, render_template
import os
import uuid
import random
import string
import base64
import qrcode
from io import BytesIO

app = Flask(__name__, template_folder='templates', static_folder='static')

# ==================== RUTAS PRINCIPALES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ==================== HERRAMIENTAS ====================

# QR Code
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

# Generador de Contraseñas
@app.route('/api/password', methods=['POST'])
def generate_password():
    length = int(request.json.get('length', 16))
    characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password = ''.join(random.choice(characters) for _ in range(length))
    return jsonify({"password": password})

# Base64
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
