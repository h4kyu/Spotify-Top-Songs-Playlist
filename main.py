import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json

# Spotify credentials
CLIENT_ID = '02f07b09c71844b298712a3846252f13'
CLIENT_SECRET = '9392b3a870cb40c19bf72669bab4d662'
REDIRECT_URI = 'http://localhost:8888/callback'

# Scopes
SCOPE = 'user-library-read playlist-modify-private'

# File to store token information
TOKEN_FILE = 'spotify_tokens.json'


# Function to authenticate and get a Spotify client
def get_spotify_client():
    print("Authenticating Spotify client...")

    # Check if token information exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token_info = json.load(f)
        # Check if token is expired
        if not SpotifyOAuth.is_token_expired(token_info):
            print("Using existing token.")
            return spotipy.Spotify(auth=token_info['access_token'])

    # If no token or expired, perform authentication
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        open_browser=True
    )

    # If no token file or token expired, authenticate
    token_info = sp_oauth.get_access_token(as_dict=True)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_info, f)

    print("Spotify client authenticated successfully.")
    return spotipy.Spotify(auth=token_info['access_token'])


# Function to get the most recent liked songs (top 10)
def get_liked_songs(sp):
    try:
        print("Fetching top 10 liked songs...")
        results = sp.current_user_saved_tracks(limit=10)
        songs = [item['track']['uri'] for item in results['items']]
        print(f"Retrieved {len(songs)} liked songs: {songs}")
        return songs
    except Exception as e:
        print(f"Error fetching liked songs: {e}")
        return []


# Function to get or create the persistent playlist
def get_or_create_playlist(sp):
    PLAYLIST_FILE = 'playlist_id.txt'

    # Check if the playlist ID file exists
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r') as f:
            playlist_id = f.read().strip()
        # Verify the playlist still exists on Spotify
        try:
            playlist = sp.playlist(playlist_id)
            print(f"Playlist found: {playlist['name']} (ID: {playlist_id})")
            return playlist_id
        except spotipy.exceptions.SpotifyException as e:
            print(f"Playlist not found. Creating a new one... ({e})")

    # If playlist doesn't exist, create a new one
    print("Creating a new playlist...")
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, 'Recently Liked Top 10', public=False)
    playlist_id = playlist['id']
    print(f"New playlist created with ID: {playlist_id}")

    # Save the new playlist ID
    with open(PLAYLIST_FILE, 'w') as f:
        f.write(playlist_id)

    return playlist_id


# Function to update the playlist with the latest liked songs
def update_playlist(sp):
    try:
        liked_songs = get_liked_songs(sp)
        if not liked_songs:
            print("No liked songs found.")
            return

        playlist_id = get_or_create_playlist(sp)
        existing_tracks = sp.playlist_tracks(playlist_id, fields='items.track.uri')['items']
        existing_uris = [item['track']['uri'] for item in existing_tracks]

        # Find songs that are not already in the playlist
        new_songs = [uri for uri in liked_songs if uri not in existing_uris]

        if new_songs:
            sp.playlist_add_items(playlist_id, new_songs)
            print(f"Added {len(new_songs)} new songs to the playlist: {new_songs}")
        else:
            print("No new songs to add.")
    except Exception as e:
        print(f"Error updating playlist: {e}")


# Main function for debugging
if __name__ == '__main__':
    print("Debugging the script...")
    sp = get_spotify_client()
    update_playlist(sp)
    print("Script completed.")
