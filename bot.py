import os
from threading import Thread
import telebot
from flask import Flask

# Récupération sécurisée depuis Render
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne 24/24 !"

def run_web():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bonjour ! Mon bot tourne 24h/24 sur Render !")

if __name__ == '__main__':
    t = Thread(target=run_web)
    t.start()
    
    bot.infinity_polling()
    
    
