from yandex_music import Client
import os
from dotenv import load_dotenv
import re

# Загрузка ключей
load_dotenv()
yandex_token = os.getenv("YANDEX_MUSIC_TOKEN")

# Инициализация клиента
client = Client(yandex_token).init()

def clean_url(url):
    """Очищаем URL от параметров (обрезаем до ?)"""
    return url.split('?')[0]

def is_yandex_music_url(url):
    """Проверяем, что это ссылка Яндекс.Музыки"""
    clean_url = url.split('?')[0]
    patterns = [
        r'https?://music\.yandex\..+',
        r'https?://yandex\..+/music/.+'
    ]
    return any(re.match(p, clean_url) for p in patterns)

def extract_info(url):
    """Основная функция для извлечения треков"""
    try:
        clean_url = url.split('?')[0]  # Очищаем URL
        
        if "track" in clean_url:
            return get_track_info(clean_url)
        elif "album" in clean_url:
            return get_album_tracks(clean_url)
        elif "playlist" in clean_url:
            return get_playlist_tracks(clean_url)
        else:
            raise ValueError("Неподдерживаемый URL Яндекс.Музыки")
    except Exception as e:
        print(f"Ошибка в extract_info: {e}")
        return []

def get_track_info(track_url):
    """Получаем информацию об одном треке"""
    try:
        clean_url = track_url.split('?')[0]
        track_id = clean_url.split('track/')[-1].split('/')[0]
        track = client.tracks([track_id])[0]
        artists = ", ".join(artist.name for artist in track.artists)
        return [f"{track.title} - {artists}"]
    except Exception as e:
        print(f"Ошибка получения трека: {e}")
        return []

def get_album_tracks(album_url):
    """Получаем все треки из альбома"""
    try:
        clean_url = album_url.split('?')[0]
        album_id = clean_url.split('album/')[-1].split('/')[0]
        album = client.albums_with_tracks(album_id)
        
        tracks = []
        for volume in album.volumes:
            for track in volume:
                artists = ", ".join(artist.name for artist in track.artists)
                tracks.append(f"{track.title} - {artists}")
        
        return tracks
    except Exception as e:
        print(f"Ошибка получения альбома: {e}")
        return []

def get_playlist_tracks(playlist_url):
    """Получаем треки из плейлиста"""
    try:
        clean_url = playlist_url.split('?')[0]
        parts = clean_url.split('/')
        user_login = parts[-3]
        playlist_id = parts[-1]
        
        playlist = client.users_playlists(playlist_id, user_login)
        
        tracks = []
        for track_short in playlist.tracks:
            track = track_short.fetch_track()
            artists = ", ".join(artist.name for artist in track.artists)
            tracks.append(f"{track.title} - {artists}")
        
        return tracks
    except Exception as e:
        print(f"Ошибка получения плейлиста: {e}")
        return []

# Тестирование
if __name__ == "__main__":
    # Примеры ссылок с параметрами
    test_track = "https://music.yandex.ru/album/1234567/track/7654321?some=param"
    test_album = "https://music.yandex.ru/album/1234567?from=search"
    test_playlist = "https://music.yandex.ru/users/yamusic-daily/playlists/1234?lang=ru"
    
    print("Трек:", get_track_info(test_track))
    print("Альбом:", get_album_tracks(test_album))
    print("Плейлист:", get_playlist_tracks(test_playlist))