import boto3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

# Spotify credentials
CLIENT_ID = '02f07b09c71844b298712a3846252f13'
CLIENT_SECRET = '9392b3a870cb40c19bf72669bab4d662'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-library-read'

# S3 bucket and object keys
S3_BUCKET = 'spotify-updater-state'
LAST_SONG_FILE = 'last_song_id.json'

s3 = boto3.client('s3')

def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))

def get_latest_liked_song(sp):
    results = sp.current_user_saved_tracks(limit=1)
    if results['items']:
        return results['items'][0]['track']['id']
    return None

def lambda_handler(event, context):
    sp = get_spotify_client()
    latest_song_id = get_latest_liked_song(sp)

    # Fetch last song ID from S3
    try:
        s3_object = s3.get_object(Bucket=S3_BUCKET, Key=LAST_SONG_FILE)
        last_saved_id = json.load(s3_object['Body'])['last_song_id']
    except s3.exceptions.NoSuchKey:
        last_saved_id = None

    # Check for new song
    if latest_song_id != last_saved_id:
        print(f"New song liked: {latest_song_id}")
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=LAST_SONG_FILE,
            Body=json.dumps({'last_song_id': latest_song_id})
        )
    else:
        print("No new songs liked.")
