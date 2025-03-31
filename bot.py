import os
import discord
from discord import app_commands
from dotenv import load_dotenv
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

    # Очередь треков
    queue = []
    is_playing = False

    #выдает сообщение при успешном запуске
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
            # Получаем текущий канал бота
            channel = voice_client.channel

            # Проверяем количество участников (исключая бота)
            members = [m for m in channel.members if not m.bot]

            # Если не осталось пользователей - отключаемся
            if len(members) == 0:
                await voice_client.disconnect()


    @client.event
    async def play_next(interaction: discord.Interaction):
        global is_playing

    #команда /hello
    @tree.command(name="hello", description="Привествует тебя")
    async def jello(interaction: discord.Interaction):
        await interaction.response.send_message("Привет, хозяин")


    #команда /join
    @tree.command(name="join", description="Присоеденить хуесоса к каналу")
    async def join(interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.move_to(channel)
            else:
                await channel.connect()
            await interaction.response.send_message(f'Пидорас присоединился к {channel.name}')
        else:
            await interaction.response.send_message("Зайди в канал даун")


    #команда /leave
    @tree.command(name="leave", description="Послать пидораса нахер из канала")
    async def leave(interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Пидорас отключился")
        else:
            await interaction.response.send_message("Ты ебнутый?")


    @tree.command(name="play", description="Заставить хуесоса петь песню")
    async def play(interaction: discord.Interaction, song_link: str):
        global is_playing
        if not interaction.voice_client:
            await interaction.invoke(join)

        queue.append(song_link)
        await interaction.send(f"Добавлено в очередь: {song_link}")

        if not is_playing:
            await play_next(interaction)


#12e1fevds
    #запускает бота
    client.run(token)