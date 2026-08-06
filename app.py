from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

from config import BOT_TOKEN

from otpinstan import (
    get_balance,
    get_history,
    get_countries,
    get_services_s2,
    get_services_s5,
    get_operators_s2,
    create_order_s2,
    create_order_s5
)

from status_checker import (
    wait_otp_server2,
    wait_otp_server5
)

from utils.order_store import save_order

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["💰 Saldo", "🌍 Negara"],
        ["🖥 Server 2", "🖥 Server 5"],
        ["📜 History", "❓ Bantuan"]
    ],
    resize_keyboard=True,
    is_persistent=True
)

SELECT_SERVER = 1
SELECT_COUNTRY = 2
SELECT_SERVICE = 3
SELECT_OPERATOR = 4
CREATE_ORDER = 5
WAIT_OTP = 6

user_session = {}
country_cache = {}
service_cache = {}
operator_cache = {}

def build_country_keyboard(countries):

    keyboard = []

    country_cache.clear()

    try:

        for country in countries["data"]:

            country_cache[country["name"]] = country["id"]

            keyboard.append([
                KeyboardButton(country["name"])
            ])

    except Exception:

        keyboard.append([
            KeyboardButton("❌ Data negara tidak tersedia")
        ])

    keyboard.append([
        KeyboardButton("🔙 Kembali")
    ])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )
    
def build_service_keyboard(services):

    keyboard = []

    service_cache.clear()

    try:

        for service in services["data"]:

            service_cache[service["name"]] = service["id"]

            keyboard.append([
                KeyboardButton(service["name"])
            ])

    except Exception:

        keyboard.append([
            KeyboardButton("❌ Tidak ada layanan")
        ])

    keyboard.append([
        KeyboardButton("🔙 Kembali")
    ])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )

def build_operator_keyboard(operators):

    keyboard = []

    operator_cache.clear()

    try:

        for operator in operators["data"]:

            operator_cache[operator["name"]] = operator["id"]

            keyboard.append([
                KeyboardButton(operator["name"])
            ])

    except Exception:

        keyboard.append([
            KeyboardButton("❌ Tidak ada operator")
        ])

    keyboard.append([
        KeyboardButton("🔙 Kembali")
    ])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )

def format_order(result):

    try:

        data = result["data"]

        return (
            f"📞 Nomor : {data['number']}\n"
            f"🆔 Order : {data['order_id']}"
        )

    except Exception:

        return str(result)

def format_otp(result):

    try:

        data = result["data"]

        return (
            "✅ OTP Diterima\n\n"
            f"📩 OTP : {data['otp']}\n"
            f"📞 Nomor : {data['number']}\n"
            f"🆔 Order : {data['order_id']}"
        )

    except Exception:

        return str(result)

def format_error(message):

    return (
        "❌ Terjadi Kesalahan\n\n"
        f"{message}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

user_session.pop(chat_id, None)

    text = (
        "🤖 *OTPInstan Telegram Bot*\n\n"
        "Selamat datang.\n"
        "Silakan pilih menu di bawah."
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = get_balance()

    await update.message.reply_text(
        f"💰 Saldo\n\n{result}",
        reply_markup=MAIN_MENU
    )

async def negara(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = get_countries()

    await update.message.reply_text(
        str(result),
        reply_markup=MAIN_MENU
    )

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = get_history()

    await update.message.reply_text(
        str(result),
        reply_markup=MAIN_MENU
    )

async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "📖 Bantuan\n\n"
        "Gunakan menu yang tersedia.\n"
        "Server 2 dan Server 5 akan ditambahkan pada langkah berikutnya."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MENU
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "💰 Saldo":
        await saldo(update, context)

    elif text == "🌍 Negara":
        await negara(update, context)

    elif text == "📜 History":
        await history(update, context)

    elif text == "❓ Bantuan":
        await bantuan(update, context)

    elif text == "🖥 Server 2":
        await update.message.reply_text(
            "🖥 Menu Server 2 sedang dibuat.",
            reply_markup=MAIN_MENU
        )

    elif text == "🖥 Server 5":
        await update.message.reply_text(
            "🖥 Menu Server 5 sedang dibuat.",
            reply_markup=MAIN_MENU
        )

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_menu
        )
    )

    print("Bot OTPInstan berjalan...")

    conversation = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^🖥 Server 2$"), server2),
        MessageHandler(filters.Regex("^🖥 Server 5$"), server5),
    ],
    states={
        SELECT_COUNTRY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, select_country)
        ],
        SELECT_SERVICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, select_service)
        ],
        SELECT_OPERATOR: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, select_operator)
        ],
    },
    fallbacks=[
        CommandHandler("start", start)
    ],
)

app.add_handler(conversation)

    app.run_polling()


if __name__ == "__main__":
    main()

async def server2(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    user_session[chat_id] = {
        "server":2
    }

    countries = get_countries()

    if otp:

    await update.message.reply_text(
        format_otp(otp),
        reply_markup=MAIN_MENU
    )

else:

    await update.message.reply_text(
        format_error("OTP tidak diterima."),
        reply_markup=MAIN_MENU
    )

    return SELECT_COUNTRY

async def server5(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    user_session[chat_id] = {
        "server":5
    }

    countries = get_countries()

    if otp:

    await update.message.reply_text(
        format_otp(otp),
        reply_markup=MAIN_MENU
    )

else:

    await update.message.reply_text(
        format_error("OTP tidak diterima."),
        reply_markup=MAIN_MENU
    )

    return SELECT_COUNTRY

async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    country_name = update.message.text

country_id = country_cache.get(country_name)

user_session[chat_id]["country"] = country_id

    if user_session[chat_id]["server"] == 2:

        services = get_services_s2(country_id)

    else:

        services = get_services_s5(country_id)

    await update.message.reply_text(
        "📱 Pilih Layanan",
        reply_markup=build_service_keyboard(services)
    )

    return SELECT_SERVICE

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    service_name = update.message.text

service_id = service_cache.get(service_name)

user_session[chat_id]["service"] = service_id

    if user_session[chat_id]["server"] == 2:

        operators = get_operators_s2(
            service,
            user_session[chat_id]["country"]
        )

        await update.message.reply_text(
            "📡 Pilih Operator",
            reply_markup=build_operator_keyboard(operators)
        )

        return SELECT_OPERATOR

    result = create_order_s5(
    user_session[chat_id]["service"],
    user_session[chat_id]["country"]
)

    if result:

    await update.message.reply_text(
        "✅ Order berhasil dibuat\n\n"
        + format_order(result)
    )

    order_id = result["data"]["order_id"]

        
save_order(
    order_id,
    chat_id
)
    await update.message.reply_text(
        "⏳ Menunggu OTP..."
    )

    otp = wait_otp_server5(order_id)

    await update.message.reply_text(
        str(otp),
        reply_markup=MAIN_MENU
    )

else:

    await update.message.reply_text(
        "❌ Gagal membuat order.",
        reply_markup=MAIN_MENU
    )

    return ConversationHandler.END

async def select_operator(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    operator_name = update.message.text

operator_id = operator_cache.get(operator_name)

user_session[chat_id]["operator"] = operator_id

    if result:

    await update.message.reply_text(
        "✅ Order berhasil dibuat\n\n"
        + format_order(result)
    )

    order_id = result["data"]["order_id"]

    await update.message.reply_text(
        "⏳ Menunggu OTP..."
    )

    otp = wait_otp_server2(order_id)

    await update.message.reply_text(
        str(otp),
        reply_markup=MAIN_MENU
    )

else:

    await update.message.reply_text(
        "❌ Gagal membuat order.",
        reply_markup=MAIN_MENU
    )

    return ConversationHandler.END
