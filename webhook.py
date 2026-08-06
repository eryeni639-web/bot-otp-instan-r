from flask import Flask, request, jsonify

from utils.helpers import (
    log_info,
    log_error
)
import os
from telegram import Bot

from config import BOT_TOKEN

from utils.order_store import (
    get_chat,
    delete_order
)

app = Flask(__name__)
bot = Bot(BOT_TOKEN)

@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.json

        order_id = data.get("order_id")

otp = data.get("otp")

chat_id = get_chat(order_id)

if chat_id:

    import asyncio

    asyncio.run(

        bot.send_message(

            chat_id,

            f"✅ OTP Diterima\n\nKode OTP : {otp}"

        )

    )

    delete_order(order_id)

        log_info(data)

        return jsonify({
            "success": True
        })

    except Exception as e:

        log_error(str(e))

        return jsonify({
            "success": False
        }), 500

def start_webhook():

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
