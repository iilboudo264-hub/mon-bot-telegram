import telebot

TOKEN = "8711108820:AAGvsyP-XZFD1n5Hv5ls1QS5FbrRCQTy56Q"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bonjour ! Mon bot tourne 24h/24 sur Render !")

bot.infinity_polling()
