from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp
import os
import uuid

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

    if not url:
        return jsonify({"error": "URL inválida"}), 400

    try:
        unique_id = str(uuid.uuid4())
        output_path = f"{DOWNLOAD_FOLDER}/{unique_id}"

        ydl_opts = {
            'outtmpl': f'{output_path}.%(ext)s',
            'quiet': True,
            'cookiesfrombrowser': 'chrome',     # ← Esta es la clave
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }

        if format_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
            })
        else:
            ydl_opts['format'] = 'best[height<=720]'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'audio':
                filename = filename.replace('.webm', '.mp3').replace('.mp4', '.mp3')

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
