import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os

# Настройки для yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloads/%(title)s.%(ext)s',
}

# Очередь треков
queue = []
is_playing = False

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f'Бот {bot.user.name} готов к работе!')


async def play_next(ctx):
    global is_playing
    if len(queue) > 0:
        is_playing = True
        url = queue.pop(0)

        # Скачивание трека
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if os.path.exists(filename):
                filename = filename.rsplit(".", 1)[0] + ".mp3"

        # Воспроизведение трека
        voice_client = ctx.voice_client
        source = discord.FFmpegPCMAudio(executable="ffmpeg", source=filename)
        voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

        await ctx.send(f"Сейчас играет: {info['title']}")
    else:
        is_playing = False
        await ctx.send("Очередь пуста!")


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Подключился к каналу {channel.name}")
    else:
        await ctx.send("Сначала зайдите в голосовой канал!")


@bot.command()
async def play(ctx, url):
    global is_playing
    if not ctx.voice_client:
        await ctx.invoke(join)

    queue.append(url)
    await ctx.send(f"Добавлено в очередь: {url}")

    if not is_playing:
        await play_next(ctx)


@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Трек пропущен!")
        await play_next(ctx)


@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    queue.clear()
    await voice_client.disconnect()
    await ctx.send("Воспроизведение остановлено и очередь очищена!")


@bot.command()
async def queue_list(ctx):
    if queue:
        message = "Очередь треков:\n" + "\n".join([f"{i + 1}. {url}" for i, url in enumerate(queue)])
        await ctx.send(message)
    else:
        await ctx.send("Очередь пуста!")


# Создаем папку для загрузок, если её нет
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Запуск бота
bot.run('YOUR_BOT_TOKEN')