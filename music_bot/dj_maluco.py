import discord
from discord.ext import commands
from collections import deque
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

music_queues, track_titles, playing, current_song = {}, {}, {}, {}

blurple = discord.Color.blurple(); red = discord.Color.red()

async def embed_create(title, description, color):
    if title is not None:
        embed = discord.Embed(title=title, description=description, color=color)
    else:
        embed = discord.Embed(description=description, color=color)
    return embed

def ensure_guild(guild_id):
    if guild_id not in music_queues:
        music_queues[guild_id] = deque()
        track_titles[guild_id] = {}
        playing[guild_id] = False

async def is_author_voice(ctx):
    if not ctx.author.voice:
        embed = await embed_create("", "❌ Você precisa estar em um canal de voz primeiro!", red)
        await ctx.send(embed=embed)
        return False
    return True  

@bot.event
async def on_ready():
    print(f"{bot.user} entrou para a festa!")

@bot.command()
async def connect_to_voice(ctx):
    if ctx.author.voice:
        canal = ctx.author.voice.channel
        await canal.connect()
    else:
        embed = await embed_create("❌ Erro", "❌ Você precisa estar em um canal de voz primeiro!", red)
        await ctx.send(embed)

async def play_next(ctx:commands.Context, guild):
    guild_id = guild.id
    ensure_guild(guild_id)
    
    # Se a fila estiver vazia, atualiza estado e retorna.
    if not music_queues[guild_id]:
        playing[guild_id] = False
        current_song[guild_id] = None
        return
    
    # Saca a próxima música da fila
    ctx_fila, url = music_queues[guild_id].popleft()
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': False,
        'outtmpl': '%(id)s.%(ext)s',  # Gera nome único baseado no ID
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        titulo = info.get("title", url)
        track_titles[url] = titulo
        current_song[guild_id] = (url, titulo)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        
    # Atualiza o estado para "playing"
    playing[guild_id] = True
    
    def after_playing(error):
        if error:
            print(f"❌Erro ao tocar música: {error}")
        # agora capturamos TANTO o ctx_fila quanto o guild
        coro = play_next(ctx_fila, guild)
        bot.loop.create_task(coro)

    voice_client.play(discord.FFmpegPCMAudio(filename), after=after_playing)
    embed = await embed_create("▶️ Agora tocando", current_song[guild_id][1], blurple)
    embed.set_footer(text=f"Pedido por {ctx_fila.author.name}")
    await ctx_fila.send(embed=embed)

@bot.command(name="p", aliases=["play"])
async def play(ctx:commands.Context, url):
    guild_id = ctx.guild.id
    ensure_guild(guild_id)

    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # Extrai título sem download prévio
    ydl_opts_info = {'quiet': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)
        titulo = info.get("title", url)

    music_queues[guild_id].append((ctx, url))
    track_titles[guild_id][url] = titulo
    thumbnail = info.get("thumbnail")
    
    embed = await embed_create("🎶 Adicionado à fila", titulo, blurple)

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    embed.set_footer(text=f"Pedido por {ctx.author.name}")
    await ctx.reply(embed=embed)
    
    if not await is_author_voice(ctx): 
        return
    
    if not voice_client:
        canal = ctx.author.voice.channel
        voice_client = await canal.connect()
  
    if not playing[guild_id]:
        await play_next(ctx, ctx.guild)

@bot.command(name="q", aliases=["queue"])
async def queue(ctx:commands.Context):
    guild_id = ctx.guild.id
    ensure_guild(guild_id)

    fila = music_queues[guild_id]
    titulos = track_titles[guild_id]

    # Aqui você pode optar por mostrar também a música atual, se desejar.
    if not fila:
        embed = await embed_create("DJ maluco bastos", "📝 A fila está vazia.", red)
        await ctx.send(embed=embed)
    else:
        embed = await embed_create("", "🎶 Músicas na fila:", blurple)

        for i, (c, url) in enumerate(fila, start=1):
            titulo = titulos.get(url, url)
            embed.add_field(name=f"{i}.", value=titulo, inline=False)
        await ctx.send(embed=embed)

@bot.command(name="n", aliases=["now"])
async def now(ctx:commands.Context):
    guild_id = ctx.guild.id
    ensure_guild(guild_id)
    
    musica = current_song.get(guild_id)
    if not musica:
        embed = await embed_create("DJ maluco bastos", "🎶 Nenhuma música está tocando no momento.", red)
        await ctx.send(embed=embed)
    else:
        url, titulo = current_song[guild_id]
        embed = await embed_create("▶️ Agora playing:", titulo, blurple)
        await ctx.send(embed=embed)
       
@bot.command(name="pause")
async def pause(ctx:commands.Context):
    if not await is_author_voice(ctx): 
        return
        
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        
        embed = await embed_create("", "⏸️ Música pausada.", blurple)
        await ctx.send(embed=embed)
    else:
        embed = await embed_create("", "❌ Nenhuma música está tocando para pausar.", red) 
        await ctx.send(embed=embed)

@bot.command(name="r", aliases=["resume"])
async def resume(ctx:commands.Context):
    if not await is_author_voice(ctx): 
        return
        
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        voice.resume()
        
        embed = await embed_create("","▶️ Música continuando.", blurple)        
        await ctx.send(embed=embed)
    else:
        embed = await embed_create("", "❌ Não há música pausada para continuar.", red)
        await ctx.send(embed=embed)

@bot.command(name="stop")
async def stop(ctx:commands.Context):
    if not await is_author_voice(ctx): 
        return
    
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice:
        voice.stop()
        embed = await embed_create("", "⏹️ Música parada.", blurple)
        await ctx.send(embed=embed)
    else:
        embed = await embed_create("", "❌ Nenhum player ativo para parar.", red)
        await ctx.send(embed)  

@bot.command(name="s", aliases=["skip"])
async def skip(ctx:commands.Context):
    if not await is_author_voice(ctx): 
        return
    
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.stop()
        embed = await embed_create("", "⏭️ Música pulada!", blurple)
        await ctx.send(embed=embed)
    else:
        embed = await embed_create("", "❌ Não tem nada playing pra pular.", red)
        await ctx.send(embed=embed)
         
@bot.command(name="w", aliases=["wipe"])
async def wipe(ctx:commands.Context):
    guild_id = ctx.guild.id
    ensure_guild(guild_id)
    fila = music_queues[guild_id]
    if not fila:
        embed = await embed_create("", "⚠️ A fila já está vazia.", red)
        await ctx.send(embed=embed)
    else:
        quantidade = len(fila)
        fila.clear()
        embed = await embed_create("🧹 Fila limpa com sucesso!", f"{quantidade} música(s) removida(s)", blurple)
        await ctx.send(embed=embed)

@bot.command(name="h", aliases=["help"])
async def help(ctx:commands.Context):
    embed = discord.Embed(
        title="📘 DJ Maluco Bastos - Comandos",
        description="Aqui estão todos os comandos disponíveis:",
        color=blurple     
    )
    embed.add_field(name="🎵 Música",
        value=(
            "`!p <url>` ou `!play <url>` - Toca uma música\n"
            "`!q` ou `!queue` - Mostra a fila\n"
            "`!n` ou `!now` - Mostra a música atual"
        ),
        inline=False
    )
    embed.add_field(
        name="⏯️ Controles de reprodução",
        value=(
            "`!pause` - Pausa a música\n"
            "`!r` ou `!resume` - Continua a música\n"
            "`!stop` - Para a música\n"
            "`!s` ou `!skip` - Pula para a próxima"   
        ),
        inline=False
    )
    embed.add_field(
        name="🧹 Fila",
        value=(
            "`!w` ou `!wipe` - Limpa a fila de músicas"
        ),
        inline=False
    )
    embed.set_footer(text="DJ Maluco está sempre no controle! 🎚️")
    await ctx.send(embed=embed)
    
@bot.command(name="quit")
async def quit(ctx):
    canal = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if canal:
        await canal.disconnect()
        embed = await embed_create("", "Tchau gente!", red)
        await ctx.send(embed=embed)
           
bot.run("SEU-TOKEN-AQUI")