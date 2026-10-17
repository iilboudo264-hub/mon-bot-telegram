import os
from threading import Thread
import telebot
from flask import Flask

TOKEN = "8711108820:AAEuMy0b1xvqCLHo2pdyBFYi5cLBy-_maw"
bot = telebot.TeleBot(TOKEN)

# Mini-serveur web pour garder Render heureux
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run_web():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bonjour ! Mon bot tourne 24h/24 sur Render !")

if __name__ == '__main__':
    # Lancer le serveur web dans un fil d'arrière-plan
    t = Thread(target=run_web)
    t.start()
    
    # Lancer le bot Telegram
    bot.infinity_polling()
    
