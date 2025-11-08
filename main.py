import spotipy
from pip._internal.cli.cmdoptions import python
import google-api-python-client
from dotenv import load_dotenv
import os

load_dotenv()

spotify_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
youtube_key = os.getenv('YOUTUBE_API_KEY')

