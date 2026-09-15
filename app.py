from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import os
import re

app = Flask(__name__)

# =========================================================
# KONFIGURASI LOGIN
# =========================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "undian-karaoke-secret-key"
)

LOGIN_USERNAME = os.environ.get(
    "LOGIN_USERNAME",
    "admin"
)

LOGIN_PASSWORD = os.environ.get(
    "LOGIN_PASSWORD",
    "admin123"
)


# =========================================================
# CEK LOGIN
# =========================================================

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not session.get("logged_in"):
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


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

    # Rapikan spasi
    name = re.sub(
        r"\s+",
        " ",
        name
    ).strip()

    # -----------------------------------------------------
    # Deteksi Artist - Title
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
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # Kalau sudah login, langsung ke halaman utama
    if session.get("logged_in"):
        return redirect(url_for("index"))

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == LOGIN_USERNAME
            and password == LOGIN_PASSWORD
        ):

            session["logged_in"] = True
            session["username"] = username

            return redirect(url_for("index"))

        return render_template(
            "login.html",
            error="Username atau password salah"
        )

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# HALAMAN UTAMA
# =========================================================

@app.route("/")
@login_required
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# API DAFTAR LAGU
# =========================================================

@app.route("/api/lagu")
@login_required
def get_songs():

    songs = load_songs()

    return jsonify(songs)


# =========================================================
# UPLOAD VIDEO
# =========================================================

@app.route("/upload", methods=["POST"])
@login_required
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


# =========================================================
# HAPUS SATU LAGU
# =========================================================

@app.route("/delete-song", methods=["POST"])
@login_required
def delete_song():

    data = request.get_json()

    if not data or "filename" not in data:

        return jsonify({
            "success": False,
            "message": "Nama file tidak ditemukan"
        })

    filename = os.path.basename(
        data["filename"]
    )

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


# =========================================================
# HAPUS SEMUA LAGU
# =========================================================

@app.route("/delete-all-songs", methods=["POST"])
@login_required
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