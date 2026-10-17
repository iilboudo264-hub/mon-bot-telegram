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
  return "Le bot VLESS est en ligne 24/24 !"


def run_web():
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message,
      "Bienvenue ! Envoyez /vless pour lancer la création guidée d'une"
      " configuration VLESS (Port 443).",
  )


# Étape 1 : Demande du nom de la configuration
@bot.message_handler(commands=["vless"])
def ask_name(message):
  chat_id = message.chat.id
  user_data[chat_id] = {}
  sent_msg = bot.send_message(
      chat_id,
      "👤 **Étape 1/2 :** Entrez le nom (remark) de votre configuration :",
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
  bot.register_next_step_handler(sent_msg, generate_vless_config)


# Étape finale : Génération propre de la configuration
def generate_vless_config(message):
  chat_id = message.chat.id
  host = message.text.strip()
  name = user_data[chat_id].get("name", "MonServeur")

  # Paramètres fixes et propres
  port = 443
  user_uuid = str(uuid.uuid4())

  # 1. Génération du lien URI standard (compatible v2rayNG, NekoBox, etc.)
  vless_link = (
      f"vless://{user_uuid}@{host}:{port}?"
      f"encryption=none&security=tls&type=ws&path=%2Fvless#{name}"
  )

  # 2. Génération d'une structure JSON exemplaire (format client Xray)
  json_config = (
      "```json\n"
      "{\n"
      '  "log": { "loglevel": "warning" },\n'
      '  "inbounds": [],\n'
      '  "outbounds": [\n'
      "    {\n"
      '      "protocol": "vless",\n'
      '      "settings": {\n'
      '        "vnext": [\n'
      "          {\n"
      f'            "address": "{host}",\n'
      f'            "port": {port},\n'
      '            "users": [\n'
      "              {\n"
      f'                "id": "{user_uuid}",\n'
      f'                "encryption": "none",\n'
      f'                "level": 0\n'
      "              }\n"
      "            ]\n"
      "          }\n"
      "        ]\n"
      "      },\n"
      '      "streamSettings": {\n'
      '        "network": "ws",\n'
      '        "security": "tls",\n'
      '        "wsSettings": {\n'
      f'          "path": "/vless"\n'
      "        }\n"
      "      }\n"
      "    }\n"
      "  ]\n"
      "}\n"
      "```"
  )

  response_text = (
      "✅ **Configuration VLESS générée avec succès !**\n\n"
      f"🔗 **Lien de partage (URI) :**\n`{vless_link}`\n\n"
      f"📄 **Modèle JSON (Client) :**\n{json_config}"
  )

  bot.reply_to(message, response_text, parse_mode="Markdown")

  # Nettoyage des données temporaires de l'utilisateur
  if chat_id in user_data:
    del user_data[chat_id]


if __name__ == "__main__":
  t = Thread(target=run_web)
  t.start()

  bot.infinity_polling()
  
    
    
    
