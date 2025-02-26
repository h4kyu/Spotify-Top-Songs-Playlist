from spotipy.oauth2 import SpotifyOAuth
import json

CLIENT_ID = '02f07b09c71844b298712a3846252f13'
CLIENT_SECRET = '9392b3a870cb40c19bf72669bab4d662'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-library-read'

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    open_browser=True
)
token_info = sp_oauth.get_access_token(as_dict=True)
with open('token.json', 'w') as f:
    json.dump(token_info, f)
print("Token saved to token.json")
