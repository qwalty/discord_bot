from yandex_music import Client
import os
from dotenv import load_dotenv
import re

# Загрузка ключей
load_dotenv()
yandex_token = os.getenv("YANDEX_MUSIC_TOKEN")

# Инициализация клиента
client = Client(yandex_token).init()

def is_yandex_music_url(url):
    """Проверяем, что это ссылка Яндекс.Музыки"""
    patterns = [
        r'https?://music\.yandex\..+',
        r'https?://yandex\..+/music/.+'
    ]
    return any(re.match(p, url) for p in patterns)

def extract_info(url):
    """Основная функция для извлечения треков"""
    try:
        if "track" in url:
            return get_track_info(url)
        elif "album" in url:
            return get_album_tracks(url)
        elif "playlist" in url:
            return get_playlist_tracks(url)
        else:
            raise ValueError("Неподдерживаемый URL Яндекс.Музыки")
    except Exception as e:
        print(f"Ошибка в extract_info: {e}")
        return []

def get_track_info(track_url):
    """Получаем информацию об одном треке"""
    try:
        # Извлекаем ID трека из URL
        track_id = track_url.split('track/')[-1].split('/')[0]
        
        # Получаем объект трека
        track = client.tracks([track_id])[0]
        
        # Формируем строку с названием и исполнителями
        artists = ", ".join(artist.name for artist in track.artists)
        return [f"{track.title} - {artists}"]
    except Exception as e:
        print(f"Ошибка получения трека: {e}")
        return []

def get_album_tracks(album_url):
    """Получаем все треки из альбома"""
    try:
        album_id = album_url.split('album/')[-1].split('/')[0]
        album = client.albums_with_tracks(album_id)
        
        tracks = []
        # Альбом может содержать несколько томов (volumes)
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
        # Разбираем URL плейлиста
        parts = playlist_url.split('/')
        user_login = parts[-3]  # Логин владельца
        playlist_id = parts[-1]  # ID плейлиста
        
        # Получаем плейлист
        playlist = client.users_playlists(playlist_id, user_login)
        
        tracks = []
        for track_short in playlist.tracks:
            # Получаем полную информацию о треке
            track = track_short.fetch_track()
            artists = ", ".join(artist.name for artist in track.artists)
            tracks.append(f"{track.title} - {artists}")
        
        return tracks
    except Exception as e:
        print(f"Ошибка получения плейлиста: {e}")
        return []

# Тестирование
if __name__ == "__main__":
    # Примеры ссылок (замените на реальные)
    test_track = "https://music.yandex.ru/album/1234567/track/7654321"
    test_album = "https://music.yandex.ru/album/1234567"
    test_playlist = "https://music.yandex.ru/users/yamusic-daily/playlists/1234"
    
    print("Трек:", get_track_info(test_track))
    print("Альбом:", get_album_tracks(test_album))
    print("Плейлист:", get_playlist_tracks(test_playlist))