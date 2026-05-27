from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp
import os
import uuid
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    format_type = request.json.get('format', 'video')
    quality = request.json.get('quality', '720')

    if not url:
        return jsonify({"error": "Ingresa una URL de YouTube"}), 400

    try:
        unique_id = str(uuid.uuid4())
        output_path = f"{DOWNLOAD_FOLDER}/{unique_id}"

        ydl_opts = {
            'outtmpl': f'{output_path}.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'retries': 5,
            'fragment_retries': 5,
            'extractor_retries': 5,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'web', 'android', 'web_embedded', 'ios_music'],
                    'skip_hls': True,
                    'po_token': True
                }
            }
        }

        # Calidad
        if format_type == 'video':
            ydl_opts['format'] = f'best[height<={quality}]/best'
        else:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if format_type == 'audio':
                filename = filename.replace('.webm', '.mp3').replace('.mp4', '.mp3')

        return send_file(filename, as_attachment=True, download_name=os.path.basename(filename))

    except Exception as e:
        error = str(e).lower()
        if any(x in error for x in ["confirm", "sign in", "bot", "cookie"]):
            msg = "YouTube está bloqueando temporalmente. Prueba con otro video o espera 10 minutos."
        else:
            msg = "Error al descargar. Inténtalo de nuevo."
        return jsonify({"error": msg}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
