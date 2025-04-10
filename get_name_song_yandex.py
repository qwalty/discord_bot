from yandex_music import Client
from yandex_music.exceptions import NotFoundError, UnauthorizedError
import os
from dotenv import load_dotenv
import re
from urllib.parse import urlparse, parse_qs

# Загрузка переменных окружения
load_dotenv()

class YandexMusicParser:
    def __init__(self):
        token = os.getenv("YANDEX_MUSIC_TOKEN")
        if not token:
            raise ValueError("YANDEX_MUSIC_TOKEN не найден в .env файле")
        
        try:
            self.client = Client(token).init()
        except UnauthorizedError:
            raise ValueError("Неверный токен Яндекс.Музыки")

    @staticmethod
    def _clean_url(url):
        """Очистка URL от параметров и якорей"""
        return url.split('?')[0].split('#')[0]

    @staticmethod
    def _extract_id(url, pattern):
        """Извлечение ID из URL"""
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def get_track_info(self, url):
        """Получение информации о треке"""
        clean_url = self._clean_url(url)
        track_id = self._extract_id(clean_url, r'track/(\d+)')
        
        if not track_id:
            return []
        
        try:
            tracks = self.client.tracks([track_id])
            if not tracks:
                return []
            
            track = tracks[0]
            artists = ", ".join(artist.name for artist in track.artists)
            return [f"{track.title} - {artists}"]
        except NotFoundError:
            return []
        except Exception as e:
            print(f"Ошибка при получении трека: {e}")
            return []

    def get_album_tracks(self, url):
        """Получение треков из альбома"""
        clean_url = self._clean_url(url)
        album_id = self._extract_id(clean_url, r'album/(\d+)')
        
        if not album_id:
            return []
        
        try:
            album = self.client.albums_with_tracks(album_id)
            if not album:
                return []
            
            tracks = []
            for volume in album.volumes or []:
                for track in volume:
                    artists = ", ".join(artist.name for artist in track.artists)
                    tracks.append(f"{track.title} - {artists}")
            
            return tracks
        except NotFoundError:
            return []
        except Exception as e:
            print(f"Ошибка при получении альбома: {e}")
            return []

    def get_playlist_tracks(self, url):
        """Получение треков из плейлиста"""
        clean_url = self._clean_url(url)
        parts = clean_url.split('/')
        
        if len(parts) < 5 or 'playlist' not in parts:
            return []
        
        playlist_id = parts[-1]
        user_login = parts[-3]
        
        try:
            playlist = self.client.users_playlists(playlist_id, user_login)
            if not playlist:
                return []
            
            tracks = []
            for track_short in playlist.tracks:
                try:
                    track = track_short.fetch_track()
                    artists = ", ".join(artist.name for artist in track.artists)
                    tracks.append(f"{track.title} - {artists}")
                except Exception as e:
                    print(f"Ошибка при обработке трека: {e}")
                    continue
            
            return tracks
        except NotFoundError:
            return []
        except Exception as e:
            print(f"Ошибка при получении плейлиста: {e}")
            return []

    def extract_info(self, url):
        """Основной метод для извлечения информации"""
        clean_url = self._clean_url(url)
        
        if 'track' in clean_url:
            return self.get_track_info(clean_url)
        elif 'album' in clean_url:
            return self.get_album_tracks(clean_url)
        elif 'playlist' in clean_url:
            return self.get_playlist_tracks(clean_url)
        else:
            return []

# Пример использования
if __name__ == "__main__":
    try:
        parser = YandexMusicParser()
        
        # Тестовые URL (замените на реальные)
        test_urls = [
            "https://music.yandex.ru/album/1234567/track/7654321",
            "https://music.yandex.ru/album/1234567",
            "https://music.yandex.ru/users/yamusic/playlists/1234",
            "https://music.yandex.ru/artist/12345"  # Неподдерживаемый тип
        ]
        
        for url in test_urls:
            print(f"\nОбработка URL: {url}")
            result = parser.extract_info(url)
            print(f"Найдено треков: {len(result)}")
            for i, track in enumerate(result[:3], 1):  # Выводим первые 3 трека
                print(f"{i}. {track}")
                
    except Exception as e:
        print(f"Ошибка инициализации: {e}")