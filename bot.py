import os
import asyncio
import discord
import yt_dlp
from discord import app_commands
from dotenv import load_dotenv
#добавить импорт списка с спотика
import get_name_song_spotify

def run_bot():
    #загружает ключ
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")


    #выдает привилегии
    intents = discord.Intents.default()
    intents.voice_states = True
    intents.members = True
    client = discord.Client(intents=intents, test_guilds=[1355813064938749993])
    tree = app_commands.CommandTree(client)

    # Очередь треков и состояние плеера
    class PlayerState:
        def __init__(self):
            self.queue = []
            self.urls = []
            self.is_playing = False

    #задаем глобально переменные через класс
    player = PlayerState()

    # Настройки для yt-dlp
    ydl_opts = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(ydl_opts)

    #Настройки для Ffmpeg
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}



    #выдает сообщение при успешном запуске бота
    @client.event
    async def on_ready():
        print(f'Бот {client.user} запущен!')

        # Синхронизация слэш-команд
        try:
            await tree.sync()
            print("Слэш-команды успешно синхронизированы.")
        except Exception as e:
            print(f"Ошибка при синхронизации команд: {e}")


    #выходит из канала если нету учасников
    @client.event
    async def on_voice_state_update(member, before, after):
        # Проверяем голосовой канал бота в гильдии
        guild = member.guild
        voice_client = guild.voice_client

        if voice_client and voice_client.is_connected():
            channel = voice_client.channel

            # Проверка кол участников (исключая бота)
            members = [m for m in channel.members if not m.bot]

            if len(members) == 0:
                player.urls.clear()
                player.is_playing = False
                await voice_client.disconnect()


    #запуск треков
    @client.event
    async def play_next(interaction):
        player.is_playing = True
        #извлекает из списка ссылку
        if len(player.queue) > 0 or len(player.urls)>0:
            song_irl=player.urls.pop(0)

            #Воспроизведение трека
            voice_client = interaction.guild.voice_client
            source = discord.FFmpegOpusAudio(executable="ffmpeg/ffmpeg.exe", **ffmpeg_options, source=song_irl)
            await interaction.followup.send("оке")
            voice_client.play(source,  after=lambda e: asyncio.run_coroutine_threadsafe(play_next(interaction), client.loop))
        else:
            player.is_playing = False


    #получение ссылок на треки
    @client.event
    async def get_links():
        if len(player.queue)>0:
            url_in_queue = player.queue.pop(0)

            #Скачивание трека
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ytdl.extract_info(url_in_queue, download=False))

            #упаковка ссылок
            if 'entries' in info:
                for entry in info['entries']:
                    if entry and entry.get('url'):
                        player.urls.append(entry['url'])
            #Если это прямая ссылка на одно видео
            elif info.get('url'):
                player.urls.append(info['url'])
        else: return


    #прост отдельная команда для присоединения бота
    @client.event
    async def join_for_play(interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.move_to(channel)
            else:
                await channel.connect()
        else:
            await interaction.followup.send("Зайди в канал даун")




    #команда /hello
    @tree.command(name="hello", description="Привествует тебя, уебок")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message("Привет, хозяин")


    #команда /join
    @tree.command(name="join", description="Присоеденить хуесоса к каналу")
    async def join(interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.move_to(channel)
            else:
                await channel.connect()
                await interaction.followup.send("я тут")
        else:
            await interaction.followup.send("Зайди в канал даун")


    #команда /leave
    @tree.command(name="leave", description="Послать пидораса нахер из канала")
    async def leave(interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Пидорас отключился")
        else:
            await interaction.response.send_message("Ты ебнутый?")


    # команда /play
    @tree.command(name="play", description="Заставить хуесоса петь песню")
    async def play(interaction: discord.Interaction, song: str):
        await interaction.response.defer()

        #я кароч не хотел засорять тут, поэт вынес отдельно присоединение к каналу
        if not player.is_playing:
            await join_for_play(interaction)
            player.queue.append(song)
            await get_links()
            await play_next(interaction)
        else:
            player.queue.append(song)
            await interaction.followup.send("добавил трек в очередь")
            await get_links()


    #команда /skip
    @tree.command(name="skip", description="Пропускает твой ебучий трек")
    async def skip(interaction: discord.Interaction):
        await interaction.response.defer()
        if (len(player.urls)) == 0 != (len(player.queue) == 0):
            await interaction.followup.send("очередь пуста гений")
        else:
            interaction.guild.voice_client.stop()
            await interaction.followup.send("оке, пропустил")
            player.is_playing = False
            await play_next(interaction)


    #команда /pause
    @tree.command(name="pause", description="Затыкает пидора пасть")
    async def pause(interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send("*молчит...*")
        interaction.guild.voice_client.pause()



    #команда /resume
    @tree.command(name="resume", description="Открывает пидору пасть")
    async def resume(interaction: discord.Interaction):
        voice=interaction.guild.voice_client
        await interaction.response.defer()
        await interaction.followup.send("*Чет говорит...*")
        voice.resume()


    #команда /clear
    @tree.command(name="clear", description="очищает очередь")
    async def clear(interaction: discord.Interaction):
        await interaction.response.defer()
        player.queue.clear()
        player.urls.clear()
        player.is_playing = False
        await interaction.followup.send("очистил очередь")



    #запускает бота
    client.run(token)