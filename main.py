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
ID_CANAL_SISTEMA = int(os.getenv('ID_CANAL_SISTEMA'))
ID_CARGO_STAFF = int(os.getenv('ID_CARGO_STAFF')) # Nova variável de cargo

ia = Groq(api_key=CHAVE_GROQ)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    canal_sys = client.get_channel(ID_CANAL_SISTEMA)
    msg = f"✅ **Sistema Raze inicializado!**\nMonitorando: `{ID_CANAL_GERAL}`\nStaff: `{ID_CANAL_STAFF}`"
    print(msg)
    if canal_sys: await canal_sys.send(msg)

@client.event
async def on_message(message):
    if message.author == client.user: return

    # --- COMANDO DE PERGUNTA DIRETA (!ia) COM TRAVA DE CARGO ---
    if message.content.startswith('!ia '):
        # Verifica se o autor tem o cargo de Staff
        tem_cargo = any(role.id == ID_CARGO_STAFF for role in message.author.roles)

        if not tem_cargo:
            await message.reply("❌ Você não tem permissão para usar a consultoria da IA.")
            return

        pergunta = message.content[4:] 
        async with message.channel.typing():
            try:
                res = ia.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Você é um consultor especializado para a Staff do servidor Raze. Responda de forma clara e direta."},
                        {"role": "user", "content": pergunta}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                resposta_direta = res.choices[0].message.content
                await message.reply(resposta_direta)
            except Exception as e:
                print(f"Erro no !ia: {e}")
        return

    # Comando de Teste Simples
    if message.content.startswith('!testestaff'):
        await message.channel.send(f'✅ Oi {message.author.name}, estou lendo este canal!')
        return

    # Processa Sugestões Automáticas (Canal Geral)
    if message.channel.id == ID_CANAL_GERAL:
        try:
            chat_completion = ia.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "Você é a equipe de suporte do servidor de GTA RP Raze. "
                            "Gere 3 opções de respostas curtas, naturais e diretas. "
                            "Não use frases repetitivas. Opção 1: Suporte. Opção 2: Regra. Opção 3: Firme."
                        )
                    },
                    {"role": "user", "content": f"Player {message.author.name} enviou: {message.content}"}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            sugestoes = chat_completion.choices[0].message.content
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
            print(f"Erro detectado: {e}")

# Inicia o servidor Web e o Bot
keep_alive()
client.run(TOKEN_DISCORD)
