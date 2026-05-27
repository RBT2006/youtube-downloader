from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import uuid
import glob

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
FFMPEG_PATH = os.path.join("ffmpeg", "bin")

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def clean_old_files():
    files = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*"))

    for file in files:
        try:
            os.remove(file)
        except:
            pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()

    url = data.get("url")
    download_type = data.get("type")

    if not url:
        return jsonify({"error": "Debes introducir una URL."}), 400

    try:
        clean_old_files()

        unique_id = str(uuid.uuid4())
        output_template = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.%(ext)s")

        if download_type == "video":
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": output_template,
                "noplaylist": True,
                "quiet": True,
                "ffmpeg_location": FFMPEG_PATH,
            }

        elif download_type == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "noplaylist": True,
                "quiet": True,
                "ffmpeg_location": FFMPEG_PATH,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }],
            }

        else:
            return jsonify({"error": "Tipo de descarga inválido."}), 400

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "download")

        downloaded_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.*"))

        if not downloaded_files:
            return jsonify({"error": "No se pudo descargar el archivo."}), 500

        final_file = downloaded_files[0]
        extension = os.path.splitext(final_file)[1]

        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").rstrip()
        final_name = f"{safe_title}{extension}"

        return send_file(
            final_file,
            as_attachment=True,
            download_name=final_name
        )

    except yt_dlp.utils.DownloadError:
        return jsonify({"error": "Video no disponible o URL inválida."}), 400

    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
