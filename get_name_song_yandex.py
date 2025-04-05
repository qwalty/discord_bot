from yandex_music import Client
import asyncio

# Инициализация клиента Яндекс Музыки
# Требуется авторизация по токену (можно получить через браузер)
client = Client()

async def setup_yandex_client(token):
    """Инициализация клиента Яндекс Музыки с токеном"""
    try:
        await client.init(token)
        return True
    except Exception as e:
        print(f"Ошибка инициализации Яндекс Музыки: {e}")
        return False

# Определяем тип контента по URL
def extract_info(url):
    if "track/" in url:
        return get_track_info(url)
    elif "album/" in url:
        return get_album_tracks_info(url)
    elif "playlist/" in url:
        return get_playlist_tracks_info(url)
    else:
        raise ValueError("Неподдерживаемый URL Яндекс Музыки")

# Получаем информацию о треке
async def get_track_info(track_url):
    try:
        track_id = track_url.split('track/')[-1].split('/')[0]
        track = await client.tracks([track_id])
        
        if not track:
            return None
            
        track = track[0]
        artists = ", ".join([artist.name for artist in track.artists])
        return f"{track.title} - {artists}"
    except Exception as e:
        print(f"Ошибка получения информации о треке: {e}")
        return None

# Получаем треки из альбома
async def get_album_tracks_info(album_url):
    try:
        album_id = album_url.split('album/')[-1].split('/')[0]
        album = await client.albums_with_tracks(album_id)
        
        if not album:
            return []
            
        tracks = []
        for volume in album.volumes:
            for track in volume:
                artists = ", ".join([artist.name for artist in track.artists])
                tracks.append(f"{track.title} - {artists}")
                
        return tracks
    except Exception as e:
        print(f"Ошибка получения треков из альбома: {e}")
        return []

# Получаем треки из плейлиста
async def get_playlist_tracks_info(playlist_url):
    try:
        # Пример URL: https://music.yandex.ru/users/USER/playlists/ID
        parts = playlist_url.split('/')
        user_login = parts[-3]
        playlist_id = parts[-1]
        
        playlist = await client.users_playlists(playlist_id, user_login)
        
        if not playlist:
            return []
            
        tracks = []
        for track_short in playlist.tracks:
            track = await track_short.fetch_track()
            artists = ", ".join([artist.name for artist in track.artists])
            tracks.append(f"{track.title} - {artists}")
            
        return tracks
    except Exception as e:
        print(f"Ошибка получения треков из плейлиста: {e}")
        return []

# Пример использования
async def main():
    # Получить токен можно из cookies браузера (значение 'yandex_login')
    token = "ВАШ_ТОКЕН_ЯНДЕКСА"
    await setup_yandex_client(token)
    
    # Примеры URL
    track_url = "https://music.yandex.ru/album/1234567/track/7654321"
    album_url = "https://music.yandex.ru/album/1234567"
    playlist_url = "https://music.yandex.ru/users/yamusic-daily/playlists/1234"
    
    # Получение информации
    track_info = await get_track_info(track_url)
    album_tracks = await get_album_tracks_info(album_url)
    playlist_tracks = await get_playlist_tracks_info(playlist_url)
    
    print("Трек:", track_info)
    print("Альбом:", album_tracks)
    print("Плейлист:", playlist_tracks)

if __name__ == "__main__":
    asyncio.run(main())