import requests

from config import OTP_API_KEY
from utils.helpers import (
    validate_api_key,
    log_info,
    log_error
)

validate_api_key(OTP_API_KEY)

BASE_URL = "https://otpinstan.com/api/reseller"

HEADERS = {
    "X-Api-Key": OTP_API_KEY
}

def api_get(endpoint, params=None):
    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            headers=HEADERS,
            params=params,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()

    except Exception as e:
        log_error(str(e))
        return None
        
def api_post(endpoint, data=None):
    try:
        response = requests.post(
            f"{BASE_URL}/{endpoint}",
            headers=HEADERS,
            data=data,
            timeout=30
        )

        return response.json()

    except Exception as e:
        log_error(str(e))
        return None


def get_balance():
    """
    Mengambil saldo akun.
    """
    log_info("Mengambil saldo akun")

    return api_get("balance.php")


def get_countries():
    """
    Mengambil daftar negara.
    """
    log_info("Mengambil daftar negara")

    return api_get("countries.php")


def get_history():
    """
    Mengambil riwayat order.
    """
    log_info("Mengambil riwayat")

    return api_get("history.php")

def cancel_order(order_id):
    """
    Membatalkan order.
    """

    log_info(f"Cancel order {order_id}")

    return api_post(
        "cancel.php",
        {
            "order_id": order_id
        }
    )


def resend_otp(order_id):
    """
    Meminta OTP dikirim ulang.
    """

    log_info(f"Resend OTP {order_id}")

    return api_post(
        "resend.php",
        {
            "order_id": order_id
        }
    )

# ==========================================================
# SERVER 2
# ==========================================================

def get_services_s2(country):

    log_info(f"Server 2 - Mengambil layanan negara {country}")

    result = api_get(
        "services.php",
        {
            "country": country
        }
    )

    print("SERVICES S2 =", result)

    return result


def get_operators_s2(service, country):
    """
    Mengambil daftar operator Server 2.
    """

    log_info(f"Server 2 - Mengambil operator {service}")

    return api_get(
        "operators.php",
        {
            "service": service,
            "country": country
        }
    )


def create_order_s2(service, country, operator=None):
    """
    Membuat order Server 2.
    """

    log_info("Server 2 - Membuat order")

    data = {
        "service": service,
        "country": country
    }

    if operator:
        data["operator"] = operator

    return api_post(
        "order.php",
        data
    )


def check_order_s2(order_id):
    """
    Mengecek status order Server 2.
    """

    log_info(f"Server 2 - Cek order {order_id}")

    return api_get(
        "check.php",
        {
            "order_id": order_id
        }
    )

# ==========================================================
# SERVER 5
# ==========================================================

def get_services_s5(country):

    log_info(f"Server 5 - Mengambil layanan negara {country}")

    result = api_get(
        "s5/services.php",
        {
            "country": country
        }
    )

    print("SERVICES S5 =", result)

    return result


def create_order_s5(service, country):
    """
    Membuat order Server 5.
    """

    log_info("Server 5 - Membuat order")

    data = {
        "service": service,
        "country": country
    }

    return api_post(
        "s5/order.php",
        data
    )


def check_order_s5(order_id):
    """
    Mengecek status order Server 5.
    """

    log_info(f"Server 5 - Cek order {order_id}")

    return api_get(
        "s5/check.php",
        {
            "order_id": order_id
        }
    )
