from yandex_music import Client
import os
from dotenv import load_dotenv
import re

# Загрузка ключей
load_dotenv()
yandex_token = os.getenv("YANDEX_MUSIC_TOKEN")

# Инициализация клиента Яндекс.Музыки
client = Client(yandex_token).init()

def extract_info(url):
    """Определяем тип контента и получаем информацию"""
    if "track/" in url:
        return get_track_info(url)
    elif "album/" in url:
        return get_album_tracks_info(url)
    elif "playlist/" in url:
        return get_playlist_tracks_info(url)
    else:
        raise ValueError("Неподдерживаемый URL Яндекс Музыки")

def get_track_info(track_url):
    """Получаем информацию о треке"""
    try:
        # Извлекаем ID трека из URL
        track_id = track_url.split('track/')[-1].split('/')[0]
        
        # Получаем данные трека
        track = client.tracks([track_id])[0]
        
        # Форматируем исполнителей
        artists = ", ".join([artist.name for artist in track.artists])
        
        # Возвращаем список с одним элементом, как в Spotify-версии
        return [f"{track.title} - {artists}"]
    except Exception as e:
        print(f"Ошибка получения трека: {e}")
        return []

def get_album_tracks_info(album_url):
    """Получаем треки из альбома"""
    try:
        # Извлекаем ID альбома
        album_id = album_url.split('album/')[-1].split('/')[0]
        
        # Получаем данные альбома
        album = client.albums_with_tracks(album_id)
        
        tracks = []
        for volume in album.volumes:
            for track in volume:
                # Форматируем данные аналогично Spotify-версии
                track_data = {
                    'track_name': track.title,
                    'artists': [artist.name for artist in track.artists]
                }
                
                # Очищаем и форматируем строку
                artists = ", ".join(track_data['artists'])
                clean_artists = artists.replace("'", "").replace("[", "").replace("]", "")
                
                tracks.append(f"{track_data['track_name']} - {clean_artists}")
        
        return tracks
    except Exception as e:
        print(f"Ошибка получения альбома: {e}")
        return []

def get_playlist_tracks_info(playlist_url):
    """Получаем треки из плейлиста"""
    try:
        # Извлекаем данные из URL
        parts = playlist_url.split('/')
        user_login = parts[-3]
        playlist_id = parts[-1]
        
        # Получаем данные плейлиста
        playlist = client.users_playlists(playlist_id, user_login)
        
        tracks = []
        for track_short in playlist.tracks:
            track = track_short.fetch_track()
            
            # Форматируем аналогично Spotify-версии
            track_data = {
                'track_name': track.title,
                'artists': [artist.name for artist in track.artists]
            }
            
            # Очищаем и форматируем строку
            artists = ", ".join(track_data['artists'])
            clean_artists = artists.replace("'", "").replace("[", "").replace("]", "")
            
            tracks.append(f"{track_data['track_name']} - {clean_artists}")
        
        return tracks
    except Exception as e:
        print(f"Ошибка получения плейлиста: {e}")
        return []

# Тестовый блок (аналогичный Spotify-версии)
if __name__ == "__main__":
    # Примеры ссылок
    test_track = "https://music.yandex.ru/album/1234567/track/7654321"
    test_album = "https://music.yandex.ru/album/1234567"
    test_playlist = "https://music.yandex.ru/users/yamusic-daily/playlists/1234"
    
    print("Трек:", get_track_info(test_track))
    print("Альбом:", get_album_tracks_info(test_album))
    print("Плейлист:", get_playlist_tracks_info(test_playlist))