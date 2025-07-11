import os
import asyncio
import discord
import yt_dlp
from discord import app_commands
from dotenv import load_dotenv
import get_name_song_spotify
import get_name_song_yandex
from text_to_speach import get_voice

def run_bot():
    #загружает ключ
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")


    #выдает привилегии
    intents = discord.Intents.all()
    intents.voice_states = True
    intents.members = True
    client = discord.Client(intents=intents)
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
        # Проверяем голосовой канал бота 
        guild = member.guild
        voice_client = guild.voice_client

        if voice_client and voice_client.is_connected():
            channel = voice_client.channel

            # Проверка кол участников (исключая бота)
            members = [m for m in channel.members if not m.bot]

            if len(members) == 0:
                player.urls.clear()
                player.queue.clear()
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
            source = discord.FFmpegOpusAudio( **ffmpeg_options, source=song_irl)
            voice_client.play(source,  after=lambda e: asyncio.run_coroutine_threadsafe(play_next(interaction), client.loop))
        else:
            player.is_playing = False


    #получение ссылок на треки
    @client.event
    async def get_links():
        if len(player.queue)>0:
            url_in_queue = player.queue.pop(0)

            #логирование запросов
            with open("logs.txt", "a", encoding='utf-8') as file:
                file.write(f"{url_in_queue}\n")


            #Извлекает ссылки из спотика
            if "spotify.com" in url_in_queue:
                songs_names= get_name_song_spotify.extract_info(url_in_queue)
                for song in songs_names:
                    request_sp = "ytsearch: " + song
                    loop = asyncio.get_event_loop()
                    sp_info= await loop.run_in_executor(None, lambda: ytdl.extract_info(request_sp, download=False))
                    # упаковка ссылок
                    if 'entries' in sp_info:
                        for entry in sp_info['entries']:
                            if entry and entry.get('url'):
                                player.urls.append(entry['url'])
                    # Если это прямая ссылка на одно видео
                    elif sp_info.get('url'):
                        player.urls.append(sp_info['url'])

            #извлекает ссылки из ютуба
            elif "youtube.com" in url_in_queue:
                loop = asyncio.get_event_loop()
                yt_info = await loop.run_in_executor(None, lambda: ytdl.extract_info(url_in_queue, download=False))
                if 'entries' in yt_info:
                    for entry in yt_info['entries']:
                        if entry and entry.get('url'):
                            player.urls.append(entry['url'])
                # Если это прямая ссылка на одно видео
                elif yt_info.get('url'):
                    player.urls.append(yt_info['url'])


            elif "yandex.ru" in url_in_queue:
                songs_names= get_name_song_yandex.get_track_info(url_in_queue)
                for song in songs_names:
                    request_yd = "ytsearch: " + song
                    loop = asyncio.get_event_loop()
                    yd_info= await loop.run_in_executor(None, lambda: ytdl.extract_info(request_yd, download=False))
                    # упаковка ссылок
                    if 'entries' in yd_info:
                        for entry in yd_info['entries']:
                            if entry and entry.get('url'):
                                player.urls.append(entry['url'])
                    # Если это прямая ссылка на одно видео
                    elif yd_info.get('url'):
                        player.urls.append(yd_info['url'])

            else:
                song= url_in_queue
                request_yd = "ytsearch: " + song
                loop = asyncio.get_event_loop()
                yt_info = await loop.run_in_executor(None, lambda: ytdl.extract_info(request_yd, download=False))
                if 'entries' in yt_info:
                    for entry in yt_info['entries']:
                        if entry and entry.get('url'):
                            player.urls.append(entry['url'])
                # Если это прямая ссылка на одно видео
                elif yt_info.get('url'):
                    player.urls.append(yt_info['url'])




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
            await interaction.followup.send("Заходи на канал, дорогой!")



    #команда /hello
    @tree.command(name="hello", description="Приветствие")
    async def hello(interaction: discord.Interaction):
        try:
            await interaction.response.send_message("ЗДРАВИЯ ЖЕЛАЮ!")
        except Exception as e:
            await interaction.followup.send('Возникла ошибка, товарищ!')
            print(e)


    #команда /join
    @tree.command(name="join", description="Присоеденить ГРОМОФОН к каналу")
    async def join(interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                if interaction.guild.voice_client:
                    await interaction.guild.voice_client.move_to(channel)
                else:
                    await channel.connect()
                    await interaction.followup.send("ГОТОВ И ЖДУ ПРИКАЗА!")
            else:
                await interaction.followup.send("ЭТО НЕВОЗМОЖНО!")
        except Exception as e:
            await interaction.followup.send('Возникла ошибка, товарищ!')
            print(e)


    #команда /leave
    @tree.command(name="leave", description="Разорвать соединение")
    async def leave(interaction: discord.Interaction):
        try:
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.disconnect()
                await interaction.response.send_message("Соединение разорвано!")
            else:
                await interaction.response.send_message("Товарищ, это невозможно!")
        except Exception as e:
            await interaction.followup.send('Возникла ошибка, товарищ!')
            print(e)


    # команда /play
    @tree.command(name="play", description="Песню ЗА-ПЕ-ВАЙ!")
    async def play(interaction: discord.Interaction, song: str):
        try:
            await interaction.response.defer()

            # я кароч не хотел засорять тут, поэт вынес отдельно присоединение к каналу
            if not player.is_playing:
                await join_for_play(interaction)
                player.queue.append(song)
                await get_links()
                await interaction.followup.send("Песню ЗА-ПЕ-ВАЙ!")
                await play_next(interaction)
            else:
                player.queue.append(song)
                await interaction.followup.send("Внёс пластинку в очередь")
                await get_links()
        except Exception as e:
            await interaction.followup.send('Возникла ошибка, товарищ!')
            print(e)



    #команда /skip
    @tree.command(name="skip", description="Перехожу к следующей!")
    async def skip(interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            if (len(player.urls)) == 0 != (len(player.queue) == 0):
                await interaction.followup.send("Нет музыки, товарищ!")
            else:
                interaction.guild.voice_client.pause()
                await interaction.followup.send("Следующее, так следующее...")
                player.is_playing = False
                await play_next(interaction)
        except Exception as e:
            await interaction.followup.send('Возникла ошибка, товарищ!')
            print(e)


    #команда /pause
    @tree.command(name="pause", description="ОТСТАВИТЬ музыку!")
    async def pause(interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            await interaction.followup.send("ЕСТЬ ОТСТАВИТЬ музыку!")
            interaction.guild.voice_client.pause()
        except Exception as e:
            await interaction.followup.send('Возникла ошибка, товарищ!')
            print(e)



    #команда /resume
    @tree.command(name="resume", description="Музыку!")
    async def resume(interaction: discord.Interaction):
        try:
            voice = interaction.guild.voice_client
            await interaction.response.defer()
            await interaction.followup.send("ЕСТЬ продолжить музыку!")
            voice.resume()
        except Exception as e:
            await interaction.followup.send('Возникла ошибка, товарищ!')
            print(e)


    #команда /clear
    @tree.command(name="clear", description="очищает очередь")
    async def clear(interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            interaction.guild.voice_client.stop()
            player.queue.clear()
            player.urls.clear()
            player.is_playing = False
            await interaction.followup.send("Пласинки убраны, товарищ!")
        except Exception as e:
            await interaction.followup.send('Возникла ошибка, товарищ!')
            print(e)


    #команда /audio
    @tree.command(name="audio", description="сдлеать из текста в войс")
    async def audio(interaction: discord.Interaction, text: str):
        try:
            if not player.is_playing:
                await join_for_play(interaction)
                voice_client = interaction.guild.voice_client
                await interaction.response.defer()
                aud = await get_voice(text)
                source =  discord.FFmpegPCMAudio(source=aud, pipe=True)
                voice_client.play(source)
                await interaction.followup.send("голос народа запущен!")
            else:
                await interaction.followup.send("не могу говорить пока играет музыка!")
        except Exception as e:
            await interaction.followup.send('Возникла ошибка, товарищ!')
            print(e)


    #запускает бота
    client.run(token)