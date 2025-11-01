import telebot
from telebot import types

# 🔑 Token va kanal ID
TOKEN = "8496235164:AAFiGPabX2CN2BvjJ3XTdHHTMj88SBDVh04"
CHANNEL_ID = -1003096445262
CHANNEL_USERNAME = "@instagram_akkuntlar"
ADMIN_ID = 7205796796  # Admin ID

bot = telebot.TeleBot(TOKEN)
user_data = {}
stats = {"users": set(), "posts": 0}


# 🔹 Obuna tekshirish funksiyasi
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ["member", "creator", "administrator"]
    except:
        return False


# 🔹 START komandasi
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    stats["users"].add(user_id)

    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_sub"))
        bot.send_message(user_id,
                         "⚠️ Botdan foydalanish uchun quyidagi kanalga obuna bo‘ling:",
                         reply_markup=markup)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🛍 InstaBozor")
    btn2 = types.KeyboardButton("💸 Akkaunt sotish")
    btn3 = types.KeyboardButton("📥 Akkaunt sotib olish")
    markup.add(btn1)
    markup.add(btn2, btn3)
    bot.send_message(user_id, "👋 Assalomu alaykum! Nima xizmat?", reply_markup=markup)


# 🔹 “Obuna bo‘ldim” tugmasi
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_subscription(call):
    if check_sub(call.message.chat.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmagansiz!")


# 🔹 Oddiy menyu tugmalari
@bot.message_handler(func=lambda m: m.text == "🛍 InstaBozor")
def bozor(m):
    bot.send_message(m.chat.id, "📢 Akkauntlar kanalimizda: https://t.me/instagram_akkuntlar")

@bot.message_handler(func=lambda m: m.text == "📥 Akkaunt sotib olish")
def sotib_olish(m):
    bot.send_message(m.chat.id, "📸 Akkaunt narxlari va rasmlar: https://t.me/instagram_akkuntlar\nMarhamat, tanlang!")


# 🔹 Akkaunt sotish jarayoni
@bot.message_handler(func=lambda m: m.text == "💸 Akkaunt sotish")
def sotish_boshlash(m):
    if not check_sub(m.chat.id):
        return start(m)
    bot.send_message(m.chat.id, "1️⃣ Akkaunt havolasini yuboring:")
    bot.register_next_step_handler(m, get_link)

def get_link(m):
    user_data[m.chat.id] = {'link': m.text, 'username': m.from_user.username or m.from_user.first_name}
    bot.send_message(m.chat.id, "2️⃣ Obunachilar sonini yozing:")
    bot.register_next_step_handler(m, get_followers)

def get_followers(m):
    user_data[m.chat.id]['followers'] = m.text
    bot.send_message(m.chat.id, "3️⃣ Akkaunt rasmlarini (1–5 tagacha) yuboring:")
    user_data[m.chat.id]['photos'] = []
    bot.register_next_step_handler(m, get_photos)

def get_photos(m):
    if m.photo:
        user_data[m.chat.id]['photos'].append(m.photo[-1].file_id)
        if len(user_data[m.chat.id]['photos']) < 5:
            bot.send_message(m.chat.id, "Yana rasm yuborishingiz mumkin yoki '✅ Tayyor' deb yozing:")
            bot.register_next_step_handler(m, get_photos)
            return
    if not m.photo and m.text != "✅ Tayyor":
        bot.send_message(m.chat.id, "Rasm yuboring yoki '✅ Tayyor' deb yozing.")
        bot.register_next_step_handler(m, get_photos)
        return
    bot.send_message(m.chat.id, "4️⃣ Akkaunt narxini so‘mda yozing:")
    bot.register_next_step_handler(m, get_price)

def get_price(m):
    user_data[m.chat.id]['price'] = m.text
    bot.send_message(m.chat.id, "5️⃣ Akkauntning afzal tomonlarini yozing:")
    bot.register_next_step_handler(m, get_features)

def get_features(m):
    info = user_data[m.chat.id]
    info['features'] = m.text

    text = (
        f"📩 *Yangi akkaunt so‘rovi*\n\n"
        f"👤 Sotuvchi: @{info['username']}\n"
        f"🔗 Havola: {info['link']}\n"
        f"👥 Obunachilar: {info['followers']}\n"
        f"💰 Narxi: {info['price']} so‘m\n"
        f"⭐ Afzalliklar: {info['features']}\n"
        f"🆔 Foydalanuvchi ID: `{m.chat.id}`"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ To‘g‘ri", callback_data=f"ok_{m.chat.id}"),
        types.InlineKeyboardButton("❌ Noto‘g‘ri", callback_data=f"no_{m.chat.id}")
    )

    # 🔸 Admin uchun rasm + ma’lumot birgalikda yuboriladi
    photos = info['photos']
    if photos:
        bot.send_photo(ADMIN_ID, photos[0], caption=text, parse_mode="Markdown", reply_markup=markup)
        for p in photos[1:]:
            bot.send_photo(ADMIN_ID, p)
    else:
        bot.send_message(ADMIN_ID, text, parse_mode="Markdown", reply_markup=markup)

    bot.send_message(m.chat.id, "✅ Rahmat! Maʼlumotlar adminga yuborildi. 24 soatda tekshiriladi.")


# 🔹 Admin javoblari
@bot.callback_query_handler(func=lambda c: c.data.startswith("ok_") or c.data.startswith("no_"))
def check_request(call):
    user_id = int(call.data.split("_")[1])
    info = user_data.get(user_id)

    if not info:
        bot.answer_callback_query(call.id, "❌ Xatolik: foydalanuvchi topilmadi.")
        return

    if call.data.startswith("ok_"):
        # Kanalga joylash
        photos = info['photos']
        caption = (
            f"📸 *Yangi akkaunt!*\n\n"
            f"🔗 {info['link']}\n"
            f"👥 Obunachilar: {info['followers']}\n"
            f"💰 Narxi: {info['price']} so‘m\n"
            f"⭐ Afzalliklar: {info['features']}"
        )

        if photos:
            bot.send_photo(CHANNEL_ID, photos[0], caption=caption, parse_mode="Markdown")
            for p in photos[1:]:
                bot.send_photo(CHANNEL_ID, p)
        else:
            bot.send_message(CHANNEL_ID, caption, parse_mode="Markdown")

        # 💬 Sotib olish tugmasi — ADMIN bilan bog‘lanadi
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 Akkaunt sotib olish", url=f"tg://user?id={ADMIN_ID}"))
        bot.send_message(CHANNEL_ID, "👇 Quyidagi tugmani bosing:", reply_markup=markup)

        bot.send_message(user_id, "✅ Akkauntingiz kanalga joylandi!")
        stats["posts"] += 1
        bot.answer_callback_query(call.id, "✅ Kanalga joylandi")

    else:
        bot.send_message(user_id, "❌ Maʼlumotlar xato. Iltimos, boshidan qayta urinib ko‘ring.")
        bot.answer_callback_query(call.id, "❌ Rad etildi")


# 🔹 Admin panel
@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if m.chat.id != ADMIN_ID:
        return
    users = len(stats["users"])
    posts = stats["posts"]
    text = (
        f"📊 *Admin panel:*\n\n"
        f"👥 Foydalanuvchilar: {users}\n"
        f"📦 Joylangan akkauntlar: {posts}\n\n"
        f"🪄 Kanal: {CHANNEL_USERNAME}"
    )
    bot.send_message(m.chat.id, text, parse_mode="Markdown")


# 🔹 Botni ishga tushirish
print("🤖 Bot ishga tushdi...")
bot.polling(none_stop=True)
