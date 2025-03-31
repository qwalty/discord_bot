import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Настройка аутентификации
client_id = 'cc85747d0be24b1d8b9f3386ec8be54c'
client_secret = '53bde1497cd64fe4be7f9e8204e406cf'

# Инициализация клиента Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



#опеределяем что это: альбом, трэк или плейлист
def extract_info(url):
    if "track/" in url:
        return get_track_info(url)
    elif "album/" in url:
        return get_album_tracks_info(url)
    elif "playlist/" in url:
        return get_playlist_tracks_info(url)
    else:
        raise ValueError("такого нету ирл")


#получаем название трека
def get_track_info(track_id):
    track = sp.track(track_id)
    artists = ", ".join([artist['name'] for artist in track['artists']])
    tracks= f"{track['name']} - {artists}"

    return tracks



#получаем названия треков из альбома
def get_album_tracks_info(album_id):
    tracks = []
    results = sp.album_tracks(album_id)
    while results:
        for item in results['items']:
            tracks.append({
                'track_name': item['name'],
                'artists': [artist['name'] for artist in item['artists']]
            })
        results = sp.next(results) if results['next'] else None

    for index, track in enumerate(tracks, start=0):

        #очистка списка исполнителей от ненужных симловов
        art = ", ".join(tracks[index]['artists'])
        clear_art = art.replace("'", "").replace("]", "")
        tracks[index]['artists'] = clear_art

        tracks[index] = f" {tracks[index]['track_name']} - {tracks[index]['artists']}"

    return tracks



#получаем названия треков из плейлиста
def get_playlist_tracks_info(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        for item in results['items']:
            track = item['track']
            if track:  # Проверка на доступность трека
                tracks.append({
                    'track_name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']]
                })
        results = sp.next(results) if results['next'] else None

    for index, track in enumerate(tracks, start=0):

        # очистка списка исполнителей от ненужных симловов
        art=", ".join(tracks[index]['artists'])
        clear_art=art.replace("'", "").replace("]", "")
        tracks[index]['artists'] = clear_art

        tracks[index]= f" {tracks[index]['track_name']} - {tracks[index]['artists']}"

    return tracks
