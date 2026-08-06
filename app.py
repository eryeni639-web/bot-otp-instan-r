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

from utils.order_store import (
    save_order,
    get_chat,
    delete_order
)

# ==========================================
# MAIN MENU
# ==========================================

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["💰 Saldo", "📜 History"],
        ["🖥 Server 2", "🖥 Server 5"],
        ["❓ Bantuan"]
    ],
    resize_keyboard=True,
    is_persistent=True
)

# ==========================================
# CONVERSATION STATE
# ==========================================

SELECT_COUNTRY = 1
SELECT_SERVICE = 2
SELECT_OPERATOR = 3

# ==========================================
# SESSION
# ==========================================

user_session = {}

country_cache = {}

service_cache = {}

operator_cache = {}

# ==========================================
# KEYBOARD NEGARA
# ==========================================

def build_country_keyboard(countries):

    keyboard = []

    country_cache.clear()

    try:

        for country in countries["data"]:

            country_cache[country["name"]] = country["id"]

            keyboard.append(
                [KeyboardButton(country["name"])]
            )

    except Exception:

        keyboard.append(
            [KeyboardButton("❌ Data tidak tersedia")]
        )

    keyboard.append(
        [KeyboardButton("🔙 Kembali")]
    )

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )

# ==========================================
# KEYBOARD LAYANAN
# ==========================================

def build_service_keyboard(services):

    keyboard = []

    service_cache.clear()

    try:

        for service in services["data"]:

            service_cache[service["name"]] = service["id"]

            keyboard.append(
                [KeyboardButton(service["name"])]
            )

    except Exception:

        keyboard.append(
            [KeyboardButton("❌ Tidak ada layanan")]
        )

    keyboard.append(
        [KeyboardButton("🔙 Kembali")]
    )

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )

# ==========================================
# KEYBOARD OPERATOR
# ==========================================

def build_operator_keyboard(operators):

    keyboard = []

    operator_cache.clear()

    try:

        for operator in operators["data"]:

            operator_cache[operator["name"]] = operator["id"]

            keyboard.append(
                [KeyboardButton(operator["name"])]
            )

    except Exception:

        keyboard.append(
            [KeyboardButton("❌ Tidak ada operator")]
        )

    keyboard.append(
        [KeyboardButton("🔙 Kembali")]
    )

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )

# ==========================================
# FORMAT ORDER
# ==========================================

def format_order(result):

    try:

        data = result["data"]

        return (
            "✅ Order Berhasil Dibuat\n\n"
            f"📞 Nomor : {data['number']}\n"
            f"🆔 Order ID : {data['order_id']}"
        )

    except Exception:

        return str(result)

# ==========================================
# FORMAT OTP
# ==========================================

def format_otp(result):

    try:

        data = result["data"]

        return (
            "🎉 OTP Berhasil Diterima\n\n"
            f"📩 OTP : {data['otp']}\n"
            f"📞 Nomor : {data['number']}\n"
            f"🆔 Order ID : {data['order_id']}"
        )

    except Exception:

        return str(result)

# ==========================================
# FORMAT ERROR
# ==========================================

def format_error(message):

    return (
        "❌ Terjadi Kesalahan\n\n"
        f"{message}"
    )

# ==========================================
# START
# ==========================================

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

# ==========================================
# MENU SALDO
# ==========================================

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = get_balance()

    await update.message.reply_text(
        f"💰 Saldo\n\n{result}",
        reply_markup=MAIN_MENU
    )

# ==========================================
# MENU HISTORY
# ==========================================

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = get_history()

    await update.message.reply_text(
        f"📜 History\n\n{result}",
        reply_markup=MAIN_MENU
    )

# ==========================================
# MENU BANTUAN
# ==========================================

async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "📖 Bantuan\n\n"
        "Pilih Server 2 atau Server 5 untuk membuat order OTP.\n\n"
        "Gunakan menu yang tersedia di keyboard."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_MENU
    )

# ==========================================
# HANDLE MENU
# ==========================================

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "💰 Saldo":
        await saldo(update, context)

    elif text == "📜 History":
        await history(update, context)

    elif text == "❓ Bantuan":
        await bantuan(update, context)

    elif text == "🖥 Server 2":
        return await server2(update, context)

    elif text == "🖥 Server 5":
        return await server5(update, context)

# ==========================================
# SERVER 2
# ==========================================

async def server2(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    user_session[chat_id] = {
        "server": 2
    }

    countries = get_countries()

    await update.message.reply_text(
        "🌍 Pilih Negara",
        reply_markup=build_country_keyboard(countries)
    )

    return SELECT_COUNTRY

async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    country_name = update.message.text

    if country_name == "🔙 Kembali":

        await start(update, context)

        return ConversationHandler.END

    country_id = country_cache.get(country_name)

    if not country_id:

        await update.message.reply_text(
            "❌ Negara tidak ditemukan."
        )

        return SELECT_COUNTRY

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

    user_session[chat_id]["country"] = country_id

    services = get_services_s2(country_id)

    await update.message.reply_text(
        "📱 Pilih Layanan",
        reply_markup=build_service_keyboard(services)
    )

    return SELECT_SERVICE

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    service_name = update.message.text

    if service_name == "🔙 Kembali":

        countries = get_countries()

        await update.message.reply_text(
            "🌍 Pilih Negara",
            reply_markup=build_country_keyboard(countries)
        )

        return SELECT_COUNTRY

    service_id = service_cache.get(service_name)

    if not service_id:

        await update.message.reply_text(
            "❌ Layanan tidak ditemukan."
        )

        return SELECT_SERVICE

    user_session[chat_id]["service"] = service_id

    if user_session[chat_id]["server"] == 2:

        operators = get_operators_s2(
            service_id,
            user_session[chat_id]["country"]
        )

        await update.message.reply_text(
            "📡 Pilih Operator",
            reply_markup=build_operator_keyboard(operators)
        )

        return SELECT_OPERATOR

    result = create_order_s5(
        service_id,
        user_session[chat_id]["country"]
    )

    if not result:

        await update.message.reply_text(
            "❌ Gagal membuat order.",
            reply_markup=MAIN_MENU
        )

        return ConversationHandler.END

    await update.message.reply_text(
        format_order(result)
    )

    order_id = result["data"]["order_id"]

    save_order(order_id, chat_id)

    await update.message.reply_text(
        "⏳ Menunggu OTP..."
    )

    otp = wait_otp_server5(order_id)

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

    delete_order(order_id)

    return ConversationHandler.END
    
await update.message.reply_text(
    format_order(result)
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

delete_order(order_id)

return ConversationHandler.END

    await update.message.reply_text(
        "📡 Pilih Operator",
        reply_markup=build_operator_keyboard(operators)
    )

    return SELECT_OPERATOR

async def select_operator(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    operator_name = update.message.text

    if operator_name == "🔙 Kembali":

        services = get_services_s2(
            user_session[chat_id]["country"]
        )

        await update.message.reply_text(
            "📱 Pilih Layanan",
            reply_markup=build_service_keyboard(services)
        )

        return SELECT_SERVICE

    operator_id = operator_cache.get(operator_name)

    if not operator_id:

        await update.message.reply_text(
            "❌ Operator tidak ditemukan."
        )

        return SELECT_OPERATOR

    user_session[chat_id]["operator"] = operator_id

    result = create_order_s2(
        user_session[chat_id]["service"],
        user_session[chat_id]["country"],
        operator_id
    )

    if not result:

        await update.message.reply_text(
            "❌ Gagal membuat order.",
            reply_markup=MAIN_MENU
        )

        return ConversationHandler.END

    await update.message.reply_text(
        format_order(result)
    )

    order_id = result["data"]["order_id"]

    save_order(
        order_id,
        chat_id
    )

    await update.message.reply_text(
        "⏳ Menunggu OTP..."
    )

    otp = wait_otp_server2(order_id)

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

    delete_order(order_id)

    return ConversationHandler.END

# ==========================================
# SERVER 5
# ==========================================

async def server5(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    user_session[chat_id] = {
        "server": 5
    }

    countries = get_countries()

    await update.message.reply_text(
        "🌍 Pilih Negara",
        reply_markup=build_country_keyboard(countries)
    )

    return SELECT_COUNTRY

# ==========================================
# MAIN
# ==========================================

def main():

    application = Application.builder().token(BOT_TOKEN).build()

    # Command
    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # Conversation Server 2 & Server 5
    conversation = ConversationHandler(

        entry_points=[
            MessageHandler(
                filters.Regex("^🖥 Server 2$"),
                server2
            ),
            MessageHandler(
                filters.Regex("^🖥 Server 5$"),
                server5
            ),
        ],

        states={

            SELECT_COUNTRY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    select_country
                )
            ],

            SELECT_SERVICE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    select_service
                )
            ],

            SELECT_OPERATOR: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    select_operator
                )
            ],

        },

        fallbacks=[
            CommandHandler(
                "start",
                start
            )
        ],

        allow_reentry=True

    )

    application.add_handler(conversation)

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_menu
        )
    )

    print("✅ OTPInstan Bot Berjalan...")

    application.run_polling()
    
    if __name__ == "__main__":
    main()
