from flask import Flask, render_template, request, jsonify
import os
import re

app = Flask(__name__)

# =========================================================
# FOLDER VIDEO
# =========================================================

UPLOAD_FOLDER = os.path.join(
    app.static_folder,
    "videos"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# FORMAT VIDEO YANG DIDUKUNG
# =========================================================

ALLOWED_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mov"
}


# =========================================================
# CEK EXTENSION
# =========================================================

def allowed_file(filename):

    extension = os.path.splitext(filename)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# =========================================================
# MEMBUAT INFORMASI LAGU DARI NAMA FILE
# =========================================================

def create_song(filename):

    # Hilangkan extension
    name = os.path.splitext(filename)[0]

    # Hilangkan informasi teknis dari nama file
    name = re.sub(
        r"_Media_[A-Za-z0-9_-]+",
        "",
        name,
        flags=re.IGNORECASE
    )

    name = re.sub(
        r"_001_\d+p",
        "",
        name,
        flags=re.IGNORECASE
    )

    name = re.sub(
        r"_\d+p",
        "",
        name,
        flags=re.IGNORECASE
    )

    # Ganti underscore menjadi spasi
    name = name.replace("_", " ")

    # Rapikan tanda -
    name = re.sub(
        r"\s+",
        " ",
        name
    ).strip()

    # -----------------------------------------------------
    # Coba deteksi:
    #
    # "Judika - Jikalau Kau Cinta"
    #
    # menjadi:
    #
    # artist = Judika
    # title  = Jikalau Kau Cinta
    # -----------------------------------------------------

    if " - " in name:

        parts = name.split(" - ", 1)

        artist = parts[0].strip()
        title = parts[1].strip()

    else:

        artist = "Karaoke"
        title = name

    return {
        "title": title,
        "artist": artist,
        "video": filename
    }


# =========================================================
# MEMBACA SEMUA VIDEO DI FOLDER
# =========================================================

def load_songs():

    songs = []

    if not os.path.exists(UPLOAD_FOLDER):
        return songs

    for filename in os.listdir(UPLOAD_FOLDER):

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        # Pastikan file
        if not os.path.isfile(filepath):
            continue

        # Pastikan format video
        if not allowed_file(filename):
            continue

        songs.append(
            create_song(filename)
        )

    # Urutkan berdasarkan judul
    songs.sort(
        key=lambda song: song["title"].lower()
    )

    return songs


# =========================================================
# HALAMAN UTAMA
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# API DAFTAR LAGU
# =========================================================

@app.route("/api/lagu")
def get_songs():

    songs = load_songs()

    return jsonify(songs)


# =========================================================
# UPLOAD VIDEO
# =========================================================

@app.route("/upload", methods=["POST"])
def upload_video():


    # -----------------------------------------------------
    # Cek apakah ada file
    # -----------------------------------------------------

    if "video" not in request.files:

        return jsonify({
            "success": False,
            "message": "Tidak ada file yang dipilih"
        })


    file = request.files["video"]


    # -----------------------------------------------------
    # Cek nama file
    # -----------------------------------------------------

    if file.filename == "":

        return jsonify({
            "success": False,
            "message": "Nama file kosong"
        })


    # -----------------------------------------------------
    # Cek extension
    # -----------------------------------------------------

    if not allowed_file(file.filename):

        return jsonify({
            "success": False,
            "message": "Format video tidak didukung"
        })


    # -----------------------------------------------------
    # Amankan nama file
    # -----------------------------------------------------

    filename = os.path.basename(
        file.filename
    )


    # -----------------------------------------------------
    # Lokasi penyimpanan
    # -----------------------------------------------------

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    # -----------------------------------------------------
    # Simpan video
    # -----------------------------------------------------

    try:

        file.save(filepath)

    except Exception as error:

        print(
            "ERROR UPLOAD:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Gagal menyimpan video"
        })


    # -----------------------------------------------------
    # Berhasil
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "message":
            "Video berhasil diupload",

        "filename":
            filename,

        "song":
            create_song(filename)

    })
@app.route("/delete-song", methods=["POST"])
def delete_song():

    data = request.get_json()

    if not data or "filename" not in data:
        return jsonify({
            "success": False,
            "message": "Nama file tidak ditemukan"
        })

    filename = os.path.basename(data["filename"])

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if not os.path.exists(filepath):
        return jsonify({
            "success": False,
            "message": "File video tidak ditemukan"
        })

    try:
        os.remove(filepath)

        return jsonify({
            "success": True,
            "message": "Lagu berhasil dihapus",
            "filename": filename
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        })

@app.route("/delete-all-songs", methods=["POST"])
def delete_all_songs():

    deleted = 0

    try:

        for filename in os.listdir(UPLOAD_FOLDER):

            filepath = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            if os.path.isfile(filepath):

                extension = os.path.splitext(
                    filename
                )[1].lower()

                if extension in {
                    ".mp4",
                    ".webm",
                    ".mov"
                }:

                    os.remove(filepath)

                    deleted += 1

        return jsonify({
            "success": True,
            "message": "Semua lagu berhasil dihapus",
            "deleted": deleted
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })

# =========================================================
# JALANKAN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5002,
        debug=True
    )