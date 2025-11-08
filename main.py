from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import time

# Load environment variables from .env file
load_dotenv()

# YouTube OAuth scopes
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# Set up Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
    scope='playlist-read-private playlist-read-collaborative'
))


def get_youtube_service():
    """Authenticate with YouTube and return service object"""
    creds = None

    # Token file stores user's access and refresh tokens
    if os.path.exists('youtube_token.pickle'):
        with open('youtube_token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Need client_secret.json from Google Cloud Console
            if not os.path.exists('client_secret.json'):
                print("\nERROR: Missing 'client_secret.json' file!")
                print("Download it from Google Cloud Console:")
                print("1. Go to https://console.cloud.google.com")
                print("2. APIs & Services > Credentials")
                print("3. Download OAuth 2.0 Client ID as 'client_secret.json'")
                print("4. Place it in the same folder as this script\n")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', YOUTUBE_SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save credentials for next run
        with open('youtube_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)


def extract_playlist_id(url):
    """Extract playlist ID from Spotify URL"""
    if "/playlist/" in url:
        playlist_id = url.split("/playlist/")[1].split("?")[0]
    else:
        playlist_id = url
    return playlist_id


def get_playlist_tracks(playlist_id):
    """Fetch all tracks from a Spotify playlist"""
    try:
        playlist = sp.playlist(playlist_id)

        playlist_name = playlist['name']
        playlist_owner = playlist['owner']['display_name']

        print(f"\nPlaylist: {playlist_name}")
        print(f"Owner: {playlist_owner}")
        print(f"Total tracks: {playlist['tracks']['total']}\n")

        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']

        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        track_list = []
        for index, item in enumerate(tracks, 1):
            track = item['track']

            if track is None:
                continue

            track_info = {
                'number': index,
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'all_artists': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'spotify_url': track['external_urls']['spotify']
            }

            track_list.append(track_info)
            print(f"{index}. {track_info['artist']} - {track_info['name']}")

        return playlist_name, track_list

    except spotipy.exceptions.SpotifyException as e:
        print(f"Error fetching playlist: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None


def search_youtube(youtube, query, max_results=5):
    """Search YouTube for a track and return video results"""
    try:
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            type='video',
            videoCategoryId='10'  # Music category
        ).execute()

        results = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']

            results.append({
                'video_id': video_id,
                'title': title,
                'channel': channel,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            })

        return results

    except Exception as e:
        print(f"    [!] YouTube search error: {e}")
        return []


def find_youtube_matches(youtube, tracks):
    """Search YouTube for each Spotify track"""
    print("\n" + "=" * 60)
    print("Searching YouTube for tracks...")
    print("=" * 60 + "\n")

    matches = []
    not_found = []

    for track in tracks:
        # Construct search query
        query = f"{track['artist']} {track['name']}"

        print(f"[*] Searching: {track['artist']} - {track['name']}")

        # Search YouTube
        results = search_youtube(youtube, query)

        if results:
            # Take the first result (most relevant)
            best_match = results[0]

            # Check if it looks like the right match
            track_lower = track['name'].lower()
            artist_lower = track['artist'].lower()
            title_lower = best_match['title'].lower()

            # Simple relevance check
            if track_lower in title_lower or artist_lower in title_lower:
                print(f"    [+] Found: {best_match['title']}")
                matches.append({
                    'track': track,
                    'youtube': best_match,
                    'confidence': 'high'
                })
            else:
                print(f"    [!] Uncertain match: {best_match['title']}")
                matches.append({
                    'track': track,
                    'youtube': best_match,
                    'confidence': 'low'
                })
        else:
            print(f"    [-] Not found")
            not_found.append(track)

        # Rate limiting - be nice to YouTube API
        time.sleep(0.5)

    print(f"\n[+] Found: {len(matches)} tracks")
    print(f"[-] Not found: {len(not_found)} tracks")

    return matches, not_found


def create_youtube_playlist(youtube, title, description=""):
    """Create a new YouTube playlist"""
    try:
        request = youtube.playlists().insert(
            part='snippet,status',
            body={
                'snippet': {
                    'title': title,
                    'description': description
                },
                'status': {
                    'privacyStatus': 'private'  # or 'public' or 'unlisted'
                }
            }
        )
        response = request.execute()

        playlist_id = response['id']
        print(f"\n[+] Created YouTube playlist: {title}")
        print(f"   Playlist ID: {playlist_id}")
        print(f"   URL: https://www.youtube.com/playlist?list={playlist_id}")

        return playlist_id

    except Exception as e:
        print(f"[-] Error creating playlist: {e}")
        return None


def add_videos_to_playlist(youtube, playlist_id, video_ids):
    """Add multiple videos to a YouTube playlist"""
    print(f"\nAdding {len(video_ids)} videos to playlist...")

    added = 0
    failed = 0

    for video_id in video_ids:
        try:
            youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            ).execute()

            added += 1
            print(f"  [+] Added video {added}/{len(video_ids)}")
            time.sleep(0.3)  # Rate limiting

        except Exception as e:
            failed += 1
            print(f"  [-] Failed to add video: {e}")

    print(f"\n[+] Successfully added {added} videos")
    if failed > 0:
        print(f"[!] Failed to add {failed} videos")

    return added


def main():
    print("=" * 60)
    print("Spotify to YouTube Playlist Converter")
    print("=" * 60)

    # Step 1: Get Spotify playlist
    url = input("\nEnter Spotify playlist URL (or playlist ID): ")
    playlist_id = extract_playlist_id(url)

    print(f"\n[*] Fetching Spotify playlist...")
    playlist_name, tracks = get_playlist_tracks(playlist_id)

    if not tracks:
        print("[-] Failed to fetch playlist.")
        return

    print(f"\n[+] Successfully fetched {len(tracks)} tracks!")

    # Step 2: Authenticate with YouTube
    print("\n[*] Authenticating with YouTube...")
    youtube = get_youtube_service()

    if not youtube:
        print("[-] YouTube authentication failed.")
        return

    print("[+] YouTube authentication successful!")

    # Step 3: Search YouTube for each track
    matches, not_found = find_youtube_matches(youtube, tracks)

    if not matches:
        print("\n[-] No YouTube matches found. Exiting.")
        return

    # Step 4: Ask user if they want to create a playlist
    print("\n" + "=" * 60)
    create = input(f"Create YouTube playlist with {len(matches)} videos? (y/n): ")

    if create.lower() != 'y':
        print("Canceled. No playlist created.")
        return

    # Step 5: Create YouTube playlist
    new_playlist_name = f"{playlist_name} (from Spotify)"
    description = f"Converted from Spotify playlist: {playlist_name}"

    yt_playlist_id = create_youtube_playlist(youtube, new_playlist_name, description)

    if not yt_playlist_id:
        print("[-] Failed to create playlist.")
        return

    # Step 6: Add videos to playlist
    video_ids = [match['youtube']['video_id'] for match in matches]
    add_videos_to_playlist(youtube, yt_playlist_id, video_ids)

    # Step 7: Summary
    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE!")
    print("=" * 60)
    print(f"[+] Converted: {len(matches)} tracks")
    print(f"[-] Not found: {len(not_found)} tracks")
    print(f"\n[*] Your YouTube playlist:")
    print(f"   https://www.youtube.com/playlist?list={yt_playlist_id}")

    if not_found:
        print(f"\n[!] Tracks not found on YouTube:")
        for track in not_found:
            print(f"   - {track['artist']} - {track['name']}")


if __name__ == "__main__":
    main()