import json
from datetime import datetime


def log_info(message):
    """
    Menampilkan log informasi.
    """
    print(f"[INFO] {datetime.now()} | {message}")


def log_error(message):
    """
    Menampilkan log error.
    """
    print(f"[ERROR] {datetime.now()} | {message}")


def success_response(data):
    """
    Response sukses.
    """
    return {
        "success": True,
        "data": data
    }


def error_response(message):
    """
    Response gagal.
    """
    return {
        "success": False,
        "error": message
    }


def pretty_json(data):
    """
    Menampilkan JSON agar mudah dibaca.
    """
    return json.dumps(data, indent=4, ensure_ascii=False)


def current_time():
    """
    Mengambil waktu sekarang.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_api_key(api_key):
    """
    Memastikan API Key tidak kosong.
    """
    if not api_key:
        raise ValueError("API Key belum diatur di file .env")

    return True
