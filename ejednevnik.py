import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from db import dobavit_zapis, poluchit_zapisi, poluchit_vse_zapisi, ochistit_dannye_polzovatelya
from analyzer import nedelnyy_otchet, mesyachnyy_otchet, generirovat_insayty, postroit_grafik_nastroeniya

TOKEN = "8926418479:AAFuRqPCUgzFJ5iPHoxtmkMyaghC3AfqSbk"
bot = telebot.TeleBot(TOKEN)

sostoyaniya_polzovateley = {}
vremennye_dannye = {}

def glavnaya_klaviatura():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("➕ Записать день"), KeyboardButton("📊 Статистика"))
    kb.add(KeyboardButton("📜 История"), KeyboardButton("⚙️ Настройки"))
    return kb

def nastroenie_klaviatura():
    kb = InlineKeyboardMarkup(row_width=5)
    for i, emodzi in enumerate(["😞", "😐", "🙂", "😊", "🤩"], 1):
        kb.add(InlineKeyboardButton(f"{i} {emodzi}", callback_data=f"nastroenie_{i}"))
    return kb

def chasy_klaviatura(tip):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    knopki = ["0.5","1","2","4","Другое"] if tip == 'ucheba' else ["6","7","8","9","Другое"]
    for k in knopki:
        kb.add(KeyboardButton(k))
    kb.add(KeyboardButton("Отмена"))
    return kb

def ochistit_sostoyanie(chat_id):
    sostoyaniya_polzovateley.pop(chat_id, None)
    vremennye_dannye.pop(chat_id, None)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "",
        reply_markup=glavnaya_klaviatura())

@bot.message_handler(commands=['add'])
def dobavit_komanda(message):
    sostoyaniya_polzovateley[message.chat.id] = 'ozhidanie_nastroeniya'
    bot.send_message(message.chat.id, "Оцени своё настроение от 1 до 5", reply_markup=nastroenie_klaviatura())

@bot.message_handler(commands=['stats'])
def statistika_komanda(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📅 За неделю", callback_data="stats_nedelya"))
    kb.add(InlineKeyboardButton("🗓 За месяц", callback_data="stats_mesyac"))
    kb.add(InlineKeyboardButton("🔍 Инсайты", callback_data="stats_insayty"))
    kb.add(InlineKeyboardButton("📉 График", callback_data="stats_grafik"))
    bot.send_message(message.chat.id, "Что хочешь узнать?", reply_markup=kb)

@bot.message_handler(commands=['history'])
def istoriya_komanda(message):
    zapisi = poluchit_vse_zapisi(message.chat.id)
    if not zapisi:
        bot.send_message(message.chat.id, "📭 У тебя пока нет записей")
        return
    tekst = "📜 Твои записи:\n"
    for z in zapisi:
        tekst += f"{z['data']} | 😊 {z['nastroenie']} | 📚 {z['chasy_ucheby']} ч | 😴 {z['chasy_sna']} ч"
        if z['kommentariy']: tekst += f" | ✏️ {z['kommentariy']}"
        tekst += "\n"
    bot.send_message(message.chat.id, tekst[:4000])

@bot.message_handler(commands=['clear'])
def ochistit_komanda(message):
    ochistit_dannye_polzovatelya(message.chat.id)
    bot.send_message(message.chat.id, "✅ Все данные удалены", reply_markup=glavnaya_klaviatura())

@bot.callback_query_handler(func=lambda call: True)
def obrabotchik_callback(call):
    cid = call.message.chat.id
    if call.data.startswith("nastroenie_"):
        nastroenie = int(call.data.split("_")[1])
        vremennye_dannye[cid] = {'nastroenie': nastroenie}
        sostoyaniya_polzovateley[cid] = 'ozhidanie_ucheby'
        bot.edit_message_text(f"Настроение: {nastroenie}/5. Теперь сколько часов ты учился/работал?", cid, call.message.message_id)
        bot.send_message(cid, "Введи число (например, 3.5) или выбери:", reply_markup=chasy_klaviatura('ucheba'))
    elif call.data == "stats_nedelya":
        zapisi = poluchit_zapisi(cid, 7)
        bot.send_message(cid, nedelnyy_otchet(zapisi))
    elif call.data == "stats_mesyac":
        zapisi = poluchit_zapisi(cid, 30)
        bot.send_message(cid, mesyachnyy_otchet(zapisi))
    elif call.data == "stats_insayty":
        zapisi = poluchit_zapisi(cid, 30)
        bot.send_message(cid, generirovat_insayty(zapisi))
    elif call.data == "stats_grafik":
        zapisi = poluchit_zapisi(cid, 30)
        buf = postroit_grafik_nastroeniya(zapisi)
        if buf:
            bot.send_photo(cid, buf, caption="📈 График изменения настроения")
        else:
            bot.send_message(cid, "Недостаточно данных для графика")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: True)
def obrabotchik_teksta(message):
    cid = message.chat.id
    sostoyanie = sostoyaniya_polzovateley.get(cid)
    tekst = message.text.strip()
    
    if sostoyanie == 'ozhidanie_ucheby':
        if tekst == "Отмена":
            ochistit_sostoyanie(cid)
            bot.send_message(cid, "Ввод отменён", reply_markup=glavnaya_klaviatura())
            return
        if tekst == "Другое":
            bot.send_message(cid, "Введи количество часов (число, например 3.5):")
            return
        try:
            val = float(tekst)
            if 0 <= val <= 24:
                vremennye_dannye[cid]['chasy_ucheby'] = val
                sostoyaniya_polzovateley[cid] = 'ozhidanie_sna'
                bot.send_message(cid, "Сколько часов ты спал? Выбери или введи:", reply_markup=chasy_klaviatura('son'))
            else:
                bot.send_message(cid, "❌ Часы должны быть от 0 до 24")
        except:
            bot.send_message(cid, "❌ Нужно ввести число (например, 4.5)")
    elif sostoyanie == 'ozhidanie_sna':
        if tekst == "Отмена":
            ochistit_sostoyanie(cid)
            bot.send_message(cid, "Ввод отменён", reply_markup=glavnaya_klaviatura())
            return
        if tekst == "Другое":
            bot.send_message(cid, "Введи количество часов сна (число):")
            return
        try:
            val = float(tekst)
            if 0 <= val <= 24:
                vremennye_dannye[cid]['chasy_sna'] = val
                sostoyaniya_polzovateley[cid] = 'ozhidanie_kommentariya'
                kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Пропустить")
                bot.send_message(cid, "Хочешь добавить комментарий? Напиши текст или нажми «Пропустить»", reply_markup=kb)
            else:
                bot.send_message(cid, "❌ Часы сна должны быть от 0 до 24")
        except:
            bot.send_message(cid, "❌ Нужно ввести число")
    elif sostoyanie == 'ozhidanie_kommentariya':
        komment = "" if tekst == "Пропустить" else tekst
        dannye = vremennye_dannye[cid]
        dobavit_zapis(cid, dannye['nastroenie'], dannye['chasy_ucheby'], dannye['chasy_sna'], komment)
        ochistit_sostoyanie(cid)
        bot.send_message(cid, "✅ Данные сохранены! Спасибо 😊", reply_markup=glavnaya_klaviatura())
    else:
        if tekst == "➕ Записать день":
            dobavit_komanda(message)
        elif tekst == "📊 Статистика":
            statistika_komanda(message)
        elif tekst == "📜 История":
            istoriya_komanda(message)
        elif tekst == "⚙️ Настройки":
            bot.send_message(cid, "⚙️ Настройки пока в разработке", reply_markup=glavnaya_klaviatura())
        else:
            bot.send_message(cid, "Используй кнопки меню. /help для справки", reply_markup=glavnaya_klaviatura())

if __name__ == "__main__":
    from db import init_db
    init_db()
    print("Бот запущен и готов к работе!")
    bot.infinity_polling()