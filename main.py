import os
import discord
from groq import Groq
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- PARTE DO FLASK (FIXO PARA O RENDER) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Raze está online!"

def run():
    # O Render usa a porta 10000 por padrão
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CÓDIGO DO BOT ---
load_dotenv()

TOKEN_DISCORD = os.getenv('DISCORD_TOKEN')
CHAVE_GROQ = os.getenv('GROQ_API_KEY')
ID_CANAL_GERAL = int(os.getenv('ID_CANAL_GERAL'))
ID_CANAL_STAFF = int(os.getenv('ID_CANAL_STAFF'))

ia = Groq(api_key=CHAVE_GROQ)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    # Ignora mensagens do próprio bot
    if message.author == client.user:
        return

    # --- COMANDO DE TESTE DIRETO ---
    if message.content.startswith('!testestaff'):
        await message.channel.send(f'✅ Oi {message.author.name}! Eu estou lendo este canal e consigo responder!')
        return
    # ------------------------------

    # Regra original do Canal Geral
    if message.channel.id != ID_CANAL_GERAL:
        return

    try:
        # (O resto do seu código da IA Groq continua igual aqui...)
        chat_completion = ia.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente de Staff de GTA RP. Gere 3 opções de resposta curtas. Use sempre 'Nós da Staff...'. Opção 1: Educada. Opção 2: Regra. Opção 3: Firme."
                },
                {"role": "user", "content": f"Player {message.author.name}: {message.content}"}
            ],
            model="llama3-8b-8192",
        )

        sugestoes = chat_completion.choices.message.content
        canal_staff = client.get_channel(ID_CANAL_STAFF)
        
        await canal_staff.send(f"**🚨 SUGESTÕES PARA: {message.author.name}**\n\n{sugestoes}")

    except Exception as e:
        print(f"Erro ao processar: {e}")

# Inicia o servidor Web e o Bot juntos
keep_alive()
client.run(TOKEN_DISCORD)
