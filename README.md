Spotify to youtube playlist converter currently no UI and runs in terminal, project developed by 2 people thus far. 

# Spotify to YouTube Playlist Converter

Convert your Spotify playlists to YouTube playlists automatically using Python.

## Features

- Fetches tracks from any Spotify playlist (public or private)
- Searches YouTube for matching videos with intelligent relevance checking
- Creates a new YouTube playlist with all found tracks
- Preserves original playlist order
- Handles unavailable tracks gracefully
- Rate limiting to respect API quotas

## Prerequisites

- Python 3.7 or higher
- A Spotify account
- A Google account with a YouTube channel

## Installation

1. Clone this repository:
```bash
git clone https://github.com/immolateds/SpotifyToYoutube.git
cd SpotifyToYoutube
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up API credentials (see Setup Guide below)

## Setup Guide

### 1. Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in and click "Create app"
3. Fill in:
   - App name: anything you want (e.g., "Playlist Converter")
   - App description: anything you want
   - Redirect URI: `http://127.0.0.1:8080/callback`
4. Click "Save"
5. Click "Settings" and copy your **Client ID** and **Client Secret**

### 2. YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project:
   - Click the project dropdown at the top
   - Click "New Project"
   - Name it (e.g., "Spotify to YouTube")
   - Click "Create"
3. Enable "YouTube Data API v3":
   - In the search bar, type "YouTube Data API v3"
   - Click on it
   - Click "Enable"
4. **Configure OAuth consent screen** (Required):
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill in required fields:
     - App name: "Spotify to YouTube Converter" (or anything)
     - User support email: Your email
     - Developer contact email: Your email
   - Click "Save and Continue"
   - **Scopes:** Skip this section (click "Save and Continue")
   - **Test users:** Click "Add Users" and add your own email address
     - ⚠️ **Important:** This allows you to use the app while it's in testing mode
     - You can add other emails if you want friends to test it
     - Only added emails will be able to authenticate
   - Click "Save and Continue" and then "Back to Dashboard"
5. Create OAuth credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Name it anything (e.g., "Desktop client")
   - Click "Create"
6. Download the JSON file and rename it to `client_secret.json`
7. Place `client_secret.json` in the project folder

**Important Notes:**
- Your app will be in "Testing" mode, which is fine for personal use
- Only emails you add as "Test users" can authenticate
- If you want anyone to use it publicly, you'd need to publish the app (requires Google verification)

### 3. Create YouTube Channel

**Important:** Your Google account needs a YouTube channel to create playlists.

1. Go to [YouTube](https://www.youtube.com)
2. Sign in with your Google account
3. Click your profile icon → "Create a channel" (if you don't have one)
4. Follow the prompts to create a basic channel

### 4. Configure Environment Variables

Create a `.env` file in the project folder with this content:

Replace the values with your actual credentials from Spotify (step 1).

## Usage

1. Run the script:
```bash
python main.py
```

2. When prompted, paste your Spotify playlist URL:

3. Your browser will open for authentication:
   - **First time:** Spotify login - click "Agree" to authorize
   - **First time:** YouTube login - click "Continue" to authorize
   - The browser may show an error page after redirect - this is normal! Just return to your terminal.

4. The script will:
   - Fetch all tracks from your Spotify playlist
   - Search for each track on YouTube using "Artist - Song Name"
   - Perform relevance checking to ensure good matches
   - Create a new private YouTube playlist
   - Add all found videos in the same order

5. When complete, you'll receive:
   - A link to your new YouTube playlist
   - A summary of tracks converted and not found
   - Details about match confidence levels

## Features Explained

### Intelligent Matching
- Uses "Artist - Song Name" search queries
- Filters results to music category
- Performs relevance checking (high/low confidence)
- Takes the most relevant result

### Rate Limiting
- Includes delays between API calls to respect quotas
- 0.5 second delay between YouTube searches
- 0.3 second delay when adding videos to playlist

### Error Handling
- Gracefully handles unavailable tracks
- Reports failed video additions
- Continues processing even if some tracks fail

## File Structure

## Security Notes

**⚠️ Never commit these files to GitHub:**
- `.env` - Contains your API credentials
- `client_secret.json` - Contains YouTube OAuth secrets
- `youtube_token.pickle` - Contains your YouTube authentication token
- `.cache` - Contains your Spotify authentication token

## Troubleshooting

### "No client_id" error
- Make sure your `.env` file exists in the project root
- Check the format: no spaces around `=`, no quotes around values
- Verify the file is named exactly `.env` (with the dot)

### "YouTube Error 403: Forbidden"
- **Check your API quota:** YouTube gives 10,000 units/day free
  - Go to Google Cloud Console → APIs & Services → Dashboard
  - Click "YouTube Data API v3" to see quota usage
- **Verify API is enabled:** YouTube Data API v3 must be enabled in Google Cloud Console

### "Access blocked: This app's request is invalid"
- You need to add your email as a test user in the OAuth consent screen
- Go to Google Cloud Console → APIs & Services → OAuth consent screen
- Scroll to "Test users" and add your email address
- If someone else is trying to use it, add their email too

### "youtubeSignupRequired" error
- You need to create a YouTube channel on your Google account
- Go to [YouTube](https://www.youtube.com) and create a channel
- Make sure you're logged in with the same account you're authenticating with

### "Invalid redirect URI" error
- Verify the redirect URI in your `.env` matches what's in Spotify Dashboard
- Use `http://127.0.0.1:8080/callback` exactly (not `localhost`)
- In Spotify Dashboard, go to Settings and check "Redirect URIs"

### Browser shows "This site can't be reached" after authentication
- This is **normal**! The script catches the authentication code from the URL
- Just return to your terminal - the script should have continued
- If it's still waiting, copy the entire URL from your browser and paste it in the terminal

### Script hangs on "Fetching Spotify playlist..."
- Check your internet connection
- Verify your Spotify credentials are correct in `.env`
- Try a different playlist URL (make sure it's public or you own it)
- Delete `.cache` file and try again

## API Limits

### YouTube API
- **Free tier:** 10,000 units per day
- **Search cost:** ~100 units per search
- **Playlist creation:** 50 units
- **Adding video:** 50 units per video
- **Estimate:** Can convert ~50-100 songs per day depending on operations

### Spotify API
- Rate limited but generous for personal use
- Typically no issues for individual users

**Tip:** If you hit YouTube quota limits, wait until the next day (quota resets at midnight Pacific Time) or request a quota increase in Google Cloud Console.

## Requirements

## How It Works

1. **Authentication:**
   - Uses OAuth 2.0 to authenticate with both Spotify and YouTube
   - Stores tokens locally for future use (you only log in once)

2. **Fetching Spotify Playlist:**
   - Retrieves all tracks from the provided playlist URL
   - Handles playlists of any size (automatically paginates)
   - Extracts track name, artist, album, and other metadata

3. **YouTube Search:**
   - Searches YouTube for each track using "Artist - Song Name"
   - Uses YouTube's music category filter for better results
   - Performs intelligent relevance checking
   - Takes the first (most relevant) result

4. **Playlist Creation:**
   - Creates a new private YouTube playlist
   - Adds all found videos in the original order
   - Reports any tracks that couldn't be found or added

## Known Limitations

- Some songs may not be available on YouTube
- Search results might occasionally return incorrect videos (live versions, covers, etc.)
- YouTube API has daily quota limits
- Playlists are created as private by default
- Match quality depends on how well artist/song names align with YouTube video titles

## License

MIT License

## Disclaimer

This tool is for personal use only. Please ensure you comply with:
- [Spotify Terms of Service](https://www.spotify.com/legal/end-user-agreement/)
- [YouTube Terms of Service](https://www.youtube.com/static?template=terms)
- [Google API Terms of Service](https://developers.google.com/terms)

This project is not affiliated with or endorsed by Spotify or YouTube.

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify all setup steps were completed correctly
3. Check that both APIs are properly enabled and configured
4. Ensure your authentication tokens are valid

---
