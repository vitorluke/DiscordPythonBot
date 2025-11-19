import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import asyncio

# Certifique-se de ter uma pasta "musicas" no diretório do bot
if not os.path.exists("musicas"):
    os.makedirs("musicas")

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id="YOUR SPOTIFY CLIENT ID", # Coloque aqui seu Client ID do Spotify
    client_secret="YOUR SPOTIFY CLIENT SECRET"# Coloque aqui seu Client Secret do spotify
)
)


queues = {}
guild_flags = {}
spotify_tasks = {}


# Configurações de Intents
intents = discord.Intents.default()
intents.message_content = True  # permite ler mensagens
command_prefix = '#'

bot = commands.Bot(command_prefix="#", intents=intents)


# Comando /ping
class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Responde com Pong!")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="help", description='Descreve os comandos')
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"{command_prefix}tocar (Toca uma música ou adiciona ela a fila)\n {command_prefix}spotify (Toca uma playlist do spotify)\n {command_prefix}pause (pausa a reprodução da música)\n {command_prefix}play (retoma a reprodução da música)\n {command_prefix}pular (pula para a próxima música)\n{command_prefix}parar (encerra a fila e disconecta o bot)\n{command_prefix}kirby (envia o kirby)\n{command_prefix}jogodavelha (inicia um jogo da velha)")

@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")

    await bot.add_cog(MyCog(bot))

    await bot.tree.sync()
    print("Comandos sincronizados")

@bot.event
async def on_message(message):
    global controle
    if message.author == bot.user:
        return
    
    # Ping
    if message.content.lower() == "#kirby":
       await message.channel.send(''' ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣤⣤⣤⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣠⡶⠒⠒⠶⣄⣠⡴⠚⠉⠁⠀⠀⠀⠀⠀⠉⠙⠳⢦⡀⠀⠀⠀⠀⠀⠀
⢠⡏⠀⠀⠀⠀⠘⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢧⡀⠀⠀⠀⠀
⢸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⢱⠀⠀⢠⠉⢡⠀⠀⠀⠀⠀⠻⡄⠀⠀⠀
⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⣾⠄⠀⢸⣦⣾⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀
⠀⠘⢧⡀⠀⠀⠀⠀⠀⠀⠈⣿⣿⠀⠀⠸⣿⡿⠀⠀⠀⠀⠀⠀⠈⠳⣄⠀
⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠈⠁⡴⠶⡆⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠹⡄
⠀⠀⠀⢷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣷
⠀⠀⠀⠸⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠇
⠀⠀⠀⣀⡿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡽⣿⡛⠁⠀
⠀⣠⢾⣭⠀⠈⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠀⢠⣝⣷⡀
⢠⡏⠘⠋⠀⠀⠀⠈⠑⠦⣄⣀⠀⠀⠀⠀⠀⣀⡠⠔⠋⠀⠀⠀⠈⠛⠃⢻
⠈⠷⣤⣀⣀⣀⣀⣀⣀⣀⣀⣤⡽⠟⠛⠿⣭⣄⣀⣀⣀⣀⣀⣀⣀⣀⣤⠞
⠀⠀⠀⠀⠉⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠀⠀⠀''')
    await bot.process_commands(message)

def play_next(ctx, guild_id):
    vc = ctx.voice_client
    if not queues.get(guild_id):
        asyncio.run_coroutine_threadsafe(vc.disconnect(), bot.loop)
        asyncio.run_coroutine_threadsafe(ctx.send("Fila finalizada!"), bot.loop)
        return

    next_song = queues[guild_id].pop(0)
    vc.play(
        discord.FFmpegPCMAudio(executable="./ffmpeg/bin/ffmpeg",
                               source=next_song['file']),
        after=lambda e: play_next(ctx, guild_id)
    )
    asyncio.run_coroutine_threadsafe(ctx.send(f"Tocando agora: {next_song['title']}"), bot.loop)

async def baixar_musica(query):
    loop = asyncio.get_event_loop()

    def run_ydl():
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "outtmpl": "musicas/%(id)s.%(ext)s",
            "cookiefile": "cookies.txt"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
            return ydl.prepare_filename(info), info["title"]

    return await loop.run_in_executor(None, run_ydl)


async def processar_spotify(ctx, link):
    guild_id = ctx.guild.id
    guild_flags[guild_id] = False  # Flag usada pelo comando parar

    # Garantir que a fila existe
    if guild_id not in queues:
        queues[guild_id] = []

    songs = []

    try:
        # --- IDENTIFICAÇÃO DO LINK ---
        if "track" in link:
            track = sp.track(link)
            query = f"{track['name']} {track['artists'][0]['name']}"
            songs.append(query)

        elif "playlist" in link:
            playlist = sp.playlist(link)
            for item in playlist['tracks']['items']:
                if item["track"] is None:
                    continue  # playlist pode ter itens apagados
                track = item["track"]
                songs.append(f"{track['name']} {track['artists'][0]['name']}")

        elif "album" in link:
            album = sp.album(link)
            for track in album["tracks"]["items"]:
                songs.append(f"{track['name']} {track['artists'][0]['name']}")

        else:
            await ctx.send("Link inválido! Use track/playlist/album.")
            return

        # --- CONECTAR AO CANAL ---
        vc = ctx.voice_client
        if not vc:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                vc = ctx.voice_client
            else:
                await ctx.send("Você precisa estar em um canal de voz!")
                return

        primeira = True

        # --- PROCESSAR TODAS AS MÚSICAS ---
        for query in songs:

            # Se o usuário usou &parar → cancelar
            if guild_flags[guild_id]:
                await ctx.send("Processamento do Spotify cancelado!")
                break

            # baixar_musica(query) → retorna (filename, título)
            filename, title = await baixar_musica(query)

            if filename is None:
                await ctx.send(f"Erro ao baixar: {query}")
                continue

            queues[guild_id].append({"title": title, "file": filename})
            await ctx.send(f"Adicionado à fila: **{title}**")

            # Começa a tocar automaticamente a primeira música da fila
            if primeira and not vc.is_playing() and not vc.is_paused():
                play_next(ctx, guild_id)
                primeira = False

    except asyncio.CancelledError:
        await ctx.send("Processamento do Spotify interrompido.")

async def jogo_da_velha(ctx):
    GAME_STATE = True
    tabuleiro = [[" " for _ in range(3)] for _ in range(3)]
    jogador = "X"

    def print_tabuleiro(tab):
        return "\n".join([" | ".join(linha) for linha in tab])

    await ctx.send(f"Iniciando Jogo Da Velha:\n```\n{print_tabuleiro(tabuleiro)}\n```")

    while GAME_STATE:
        await ctx.send(f"Vez do jogador {jogador}! Escolha posição (linha,coluna) 0-2:")

        def checar(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for("message", check=checar, timeout=60.0)
            linha, coluna = map(int, msg.content.split(","))
        except Exception:
            await ctx.send("Entrada inválida ou tempo esgotado. Encerrando jogo.")
            break

        if tabuleiro[linha][coluna] == " ":
            tabuleiro[linha][coluna] = jogador
        else:
            await ctx.send("Posição ocupada! Tente novamente.")
            continue

        await ctx.send(f"```\n{print_tabuleiro(tabuleiro)}\n```")

        # Verifica vitória
        vencedor = None
        for i in range(3):
            if tabuleiro[i][0] == tabuleiro[i][1] == tabuleiro[i][2] != " ":
                vencedor = jogador
            if tabuleiro[0][i] == tabuleiro[1][i] == tabuleiro[2][i] != " ":
                vencedor = jogador
        if tabuleiro[0][0] == tabuleiro[1][1] == tabuleiro[2][2] != " ":
            vencedor = jogador
        if tabuleiro[0][2] == tabuleiro[1][1] == tabuleiro[2][0] != " ":
            vencedor = jogador

        if vencedor:
            await ctx.send(f"Fim de jogo! Vencedor: {vencedor}")
            GAME_STATE = False
            break

        # Verifica empate
        if all(tabuleiro[i][j] != " " for i in range(3) for j in range(3)):
            await ctx.send("Empate! Tabuleiro cheio.")
            GAME_STATE = False
            break

        # Alterna jogador
        jogador = "O" if jogador == "X" else "X"


@bot.command()
async def jogodavelha(ctx):
    asyncio.create_task(jogo_da_velha(ctx))




# Comando de voz: entrar em canal de voz
@bot.command()
async def entrar(ctx):
    if ctx.author.voice:
        canal = ctx.author.voice.channel
        await canal.connect()
        await ctx.send(f"Conectado no canal {canal}")
    else:
        await ctx.send("Você precisa estar em um canal de voz!")

# Comando para o bot sair do canal de voz
@bot.command()
async def sair(ctx):
    guild_id = ctx.guild.id
    vc = ctx.voice_client

    # Seta flag do servidor para interromper adições
    guild_flags[guild_id] = True

    if vc:
        await vc.disconnect()
        queues[guild_id] = []
        await ctx.send("Desconectado do canal de voz e fila limpa!")
    else:
        await ctx.send("Não estou conectado em nenhum canal de voz!")

    # Reseta flag para este servidor
    guild_flags[guild_id] = False
@bot.command()
async def tocar(ctx, *, search):
    guild_id = ctx.guild.id
    if guild_id not in queues:
        queues[guild_id] = []

    # Conectar ao canal de voz se não estiver
    vc = ctx.voice_client
    if not vc:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            vc = ctx.voice_client
        else:
            await ctx.send("Você precisa estar em um canal de voz!")
            return

    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True, 'outtmpl': 'musicas/%(id)s.%(ext)s','cookiefile': "cookies.txt"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{search}", download=True)['entries'][0]
        filename = ydl.prepare_filename(info)
        queues[guild_id].append({'title': info['title'], 'file': filename})
        await ctx.send(f"Adicionado à fila: {info['title']}")

    # Se nada estiver tocando, toca imediatamente
    if not vc.is_playing():
        play_next(ctx, guild_id)


@bot.command()
async def spotify(ctx, link):
    guild_id = ctx.guild.id

    # Cancela task anterior
    if guild_id in spotify_tasks:
        spotify_tasks[guild_id].cancel()
        del spotify_tasks[guild_id]

    task = asyncio.create_task(processar_spotify(ctx, link))
    spotify_tasks[guild_id] = task

# COMANDOS DE CONTROLE
@bot.command()
async def pular(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()  # Isso chama a função play_next automaticamente
        await ctx.send("Música pulada!")
    else:
        await ctx.send("Não estou tocando nada!")

@bot.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("Música pausada!")
    else:
        await ctx.send("Não estou tocando nada!")
@bot.command()
async def play(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("Música retomada!")
    else:
        await ctx.send("Não há música pausada!")



@bot.command()
async def fila(ctx):
    guild_queue = queues.get(ctx.guild.id, [])
    if not guild_queue:
        await ctx.send("A fila está vazia!")
        return

    mensagem = "Fila atual:\n"
    for i, song in enumerate(guild_queue, 1):
        mensagem += f"{i}. {song['title']}\n"
    await ctx.send(mensagem)


@bot.command()
async def parar(ctx):
    guild_id = ctx.guild.id
    vc = ctx.voice_client

    guild_flags[guild_id] = True

    # Cancela task do Spotify
    if guild_id in spotify_tasks:
        spotify_tasks[guild_id].cancel()
        del spotify_tasks[guild_id]

    if vc:
        vc.stop()
        await vc.disconnect()

    queues[guild_id] = []

    await ctx.send("Música parada e fila limpa!")
    guild_flags[guild_id] = False

@bot.command()
async def chutar(ctx, usuario: discord.Member):
    autor = ctx.author.mention
    alvo = usuario.mention
    await ctx.send("{} chutou {}".format(autor,alvo))

bot.run("YOUR DISCORD BOT TOKEN")
