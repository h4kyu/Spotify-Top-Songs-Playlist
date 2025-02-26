import boto3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

# Spotify credentials
CLIENT_ID = '02f07b09c71844b298712a3846252f13'
CLIENT_SECRET = '9392b3a870cb40c19bf72669bab4d662'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'playlist-modify-private user-library-read'

# S3 bucket and object keys
S3_BUCKET = 'spotify-updater-state'
PLAYLIST_FILE = 'playlist_id.json'

s3 = boto3.client('s3')

def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))

def get_or_create_playlist(sp):
    try:
        s3_object = s3.get_object(Bucket=S3_BUCKET, Key=PLAYLIST_FILE)
        playlist_id = json.load(s3_object['Body'])['playlist_id']
        sp.playlist(playlist_id)  # Verify playlist exists
        return playlist_id
    except:
        pass

    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, 'Recently Liked Top 10', public=False)
    playlist_id = playlist['id']
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=PLAYLIST_FILE,
        Body=json.dumps({'playlist_id': playlist_id})
    )
    return playlist_id

def update_playlist(sp, playlist_id):
    results = sp.current_user_saved_tracks(limit=10)
    liked_songs = [item['track']['uri'] for item in results['items']]
    sp.playlist_replace_items(playlist_id, liked_songs)
    print(f"Playlist updated with {len(liked_songs)} songs!")

def lambda_handler(event, context):
    sp = get_spotify_client()
    playlist_id = get_or_create_playlist(sp)
    update_playlist(sp, playlist_id)
