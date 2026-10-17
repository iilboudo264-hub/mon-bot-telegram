import os
import uuid
from threading import Thread
import telebot
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask("")

# Dictionnaire pour stocker temporairement les réponses de chaque utilisateur
user_data = {}


@app.route("/")
def home():
  return "Le bot DarkTunnel est en ligne 24/24 !"


def run_web():
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message,
      "Bienvenue ! Envoyez /vless pour lancer la création guidée d'une"
      " configuration DarkTunnel (Port 443).",
  )


# Étape 1 : Demande du nom de la configuration
@bot.message_handler(commands=["vless"])
def ask_name(message):
  chat_id = message.chat.id
  user_data[chat_id] = {}
  sent_msg = bot.send_message(
      chat_id,
      "👤 **Étape 1/2 :** Entrez le nom de votre configuration :",
      parse_mode="Markdown",
  )
  bot.register_next_step_handler(sent_msg, ask_host)


# Étape 2 : Demande de l'adresse du serveur / domaine
def ask_host(message):
  chat_id = message.chat.id
  user_data[chat_id]["name"] = message.text

  sent_msg = bot.send_message(
      chat_id,
      "🌐 **Étape 2/2 :** Entrez l'adresse de votre serveur ou domaine (ex:"
      " `votre-app.onrender.com`) :",
      parse_mode="Markdown",
  )
  bot.register_next_step_handler(sent_msg, generate_darktunnel_config)


# Étape finale : Génération propre de la configuration DarkTunnel
def generate_darktunnel_config(message):
  chat_id = message.chat.id
  host = message.text.strip()
  name = user_data[chat_id].get("name", "MonServeur")

  # Paramètres fixes
  port = 443
  user_uuid = str(uuid.uuid4())

  # Lien de secours optionnel
  vless_link = (
      f"vless://{user_uuid}@{host}:{port}?"
      f"encryption=none&security=tls&type=ws&path=%2Fvless#{name}"
  )

  # Modèle de payload DarkTunnel
  darktunnel_payload = (
      "```text\n"
      "GET / HTTP/1.1[crlf]"
      f"Host: {host}[crlf]"
      "Upgrade: websocket[crlf]"
      "Connection: Upgrade[crlf]"
      "User-Agent: [ua][crlf]"
      "[crlf]\n"
      "```"
  )

  response_text = (
      "✅ **Configuration DarkTunnel générée avec succès !**\n\n"
      f"👤 **Nom :** `{name}`\n"
      f"🌐 **Serveur / Host :** `{host}`\n"
      f"🔌 **Port :** `{port}` (SSL/TLS)\n\n"
      f"📋 **Payload WebSocket :**\n{darktunnel_payload}\n\n"
      f"🔗 **Lien VLESS / WebSocket associé :**\n`{vless_link}`"
  )

  bot.reply_to(message, response_text, parse_mode="Markdown")

  # Nettoyage des données temporaires de l'utilisateur
  if chat_id in user_data:
    del user_data[chat_id]


if __name__ == "__main__":
  t = Thread(target=run_web)
  t.start()

  bot.infinity_polling()
  
