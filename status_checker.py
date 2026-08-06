import time

from otpinstan import (
    check_order_s2,
    check_order_s5
)

from utils.helpers import (
    log_info,
    log_error
)

CHECK_INTERVAL = 5
MAX_RETRY = 60

def wait_otp_server2(order_id):
    """
    Menunggu OTP Server 2.
    """

    log_info(f"Menunggu OTP Server 2 : {order_id}")

    for _ in range(MAX_RETRY):

        result = check_order_s2(order_id)

        if result:

            return result

        time.sleep(CHECK_INTERVAL)

    log_error("Timeout Server 2")

    return None

def wait_otp_server5(order_id):
    """
    Menunggu OTP Server 5.
    """

    log_info(f"Menunggu OTP Server 5 : {order_id}")

    for _ in range(MAX_RETRY):

        result = check_order_s5(order_id)

        if result:

            return result

        time.sleep(CHECK_INTERVAL)

    log_error("Timeout Server 5")

    return None
