import os
import discord
from groq import Groq
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- WEB SERVER PARA O RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Raze Sistema ON!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- CONFIGURAÇÕES ---
load_dotenv()
TOKEN_DISCORD = os.getenv('DISCORD_TOKEN')
CHAVE_GROQ = os.getenv('GROQ_API_KEY')
ID_CANAL_GERAL = int(os.getenv('ID_CANAL_GERAL'))
ID_CANAL_STAFF = int(os.getenv('ID_CANAL_STAFF'))
ID_CANAL_SISTEMA = int(os.getenv('ID_CANAL_SISTEMA')) # NOVO CANAL

ia = Groq(api_key=CHAVE_GROQ)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    canal_sys = client.get_channel(ID_CANAL_SISTEMA)
    msg = f"✅ **Sistema Raze inicializado!**\nMonitorando Geral: `{ID_CANAL_GERAL}`\nEnviando Sugestões: `{ID_CANAL_STAFF}`"
    print(msg)
    if canal_sys: await canal_sys.send(msg)

@client.event
async def on_message(message):
    if message.author == client.user: return

    # Comando de Teste
    if message.content.startswith('!testestaff'):
        await message.channel.send(f'✅ Oi {message.author.name}, estou lendo este canal!')
        return

    # Se a mensagem for no Geral, processa a IA
    if message.channel.id == ID_CANAL_GERAL:
        try:
        chat_completion = ia.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é Staff de GTA RP. Gere 3 opções curtas com 'Nós da Staff...'."},
                {"role": "user", "content": f"Player {message.author.name}: {message.content}"}
            ],
            model="llama-3.3-70b-versatile",
        )
        
        # --- A CORREÇÃO ESTÁ NESTA LINHA ABAIXO ---
        sugestoes = chat_completion.choices[0].message.content
        # ------------------------------------------

        canal_staff = client.get_channel(ID_CANAL_STAFF)
            
            embed = discord.Embed(title="🚨 NOVA MENSAGEM NO GERAL", color=0x2f3136)
            embed.add_field(name="Autor", value=message.author.mention, inline=True)
            embed.add_field(name="Fala", value=message.content, inline=False)
            embed.add_field(name="Sugestões da IA", value=sugestoes, inline=False)
            await canal_staff.send(embed=embed)

        except Exception as e:
            canal_sys = client.get_channel(ID_CANAL_SISTEMA)
            erro_msg = f"⚠️ **ERRO NA IA:**\n```{e}```"
            if canal_sys: await canal_sys.send(erro_msg)
            print(erro_msg)

# Inicia tudo
keep_alive()
client.run(TOKEN_DISCORD)
