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
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    # Regra 1: Ignora se for mensagem de outro bot
    # Regra 2: Só lê se for no canal geral que você configurou
    if message.author.bot or message.channel.id != ID_CANAL_GERAL:
        return

    try:
        # O Groq processa a mensagem do jogador de forma ultra rápida
        chat_completion = ia.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente de Staff de um servidor de GTA RP chamado Raze. "
                        "Gere 3 opções de resposta curtas e limpas baseadas na mensagem do jogador. "
                        "Todas as opções DEVEM começar com 'Nós da Staff...'. "
                        "Opção 1: Educada/Prestativa. "
                        "Opção 2: Informativa/Regra. "
                        "Opção 3: Firme/Autoridade (para casos de desrespeito ou chatice)."
                    )
                },
                {
                    "role": "user",
                    "content": f"Jogador {message.author.name} enviou: {message.content}",
                }
            ],
            model="llama3-8b-8192", # Modelo gratuito e veloz
        )

        sugestoes = chat_completion.choices.message.content
        canal_staff = client.get_channel(ID_CANAL_STAFF)
        
        # Monta o Log bonitão no canal de Staff
        embed = discord.Embed(title="🚨 NOVA MENSAGEM DETECTADA", color=0xff0000)
        embed.add_field(name="Player", value=message.author.name, inline=True)
        embed.add_field(name="Mensagem Original", value=message.content, inline=False)
        embed.add_field(name="Sugestões de Resposta", value=sugestoes, inline=False)
        embed.set_footer(text="Copie e cole a melhor opção no chat geral.")

        await canal_staff.send(embed=embed)

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

# Inicia o servidor Web e o Bot juntos
keep_alive()
client.run(TOKEN_DISCORD)
