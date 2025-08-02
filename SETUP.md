# Quick Setup Guide

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Application**
   
   **Windows:**
   ```bash
   start.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   
   **Manual:**
   ```bash
   python app.py
   ```

3. **Open Your Browser**
   Navigate to: http://localhost:5000

## 🔧 Platform Setup

### Spotify Setup (Required for Spotify transfers)

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add `http://localhost:5000/callback` to Redirect URIs
4. Copy your Client ID and Client Secret
5. Enter them in the web interface when prompted

### Amazon Music Setup (Required for Amazon Music transfers)

1. Go to [Amazon Developer Console](https://developer.amazon.com/)
2. Sign in with your Amazon account
3. Create a new security profile
4. Navigate to Amazon Music API section
5. Create a new app for Amazon Music
6. Configure OAuth 2.0 settings with scopes: `music:playlist_read` and `music:playlist_write`
7. Copy your Client ID and Client Secret
8. Enter them in the web interface when prompted

### YouTube Music Setup

YouTube Music doesn't require explicit API credentials for basic operations, but you may need to authenticate through the web interface.

## 📱 Using the Tool

1. **Select Source Platform** - Choose where your playlist is currently located
2. **Enter Credentials** - If required (Spotify and Amazon Music need API credentials)
3. **Select Playlist** - Choose which playlist to transfer
4. **Select Destination** - Choose where to transfer the playlist to
5. **Start Transfer** - Click the transfer button and monitor progress

## 🖥️ Command Line Interface

For advanced users, you can also use the CLI:

```bash
# List supported platforms
python cli.py platforms

# List playlists from Spotify
python cli.py playlists --platform spotify --client-id YOUR_ID --client-secret YOUR_SECRET

# List playlists from Amazon Music
python cli.py playlists --platform amazon_music --client-id YOUR_ID --client-secret YOUR_SECRET

# Transfer a playlist
python cli.py transfer --source spotify --dest amazon_music --playlist-id PLAYLIST_ID
```

## 🆘 Troubleshooting

- **"No module named 'spotipy'"**: Run `pip install -r requirements.txt`
- **Spotify authentication fails**: Verify your Client ID and Secret are correct
- **Amazon Music authentication fails**: Verify your Client ID and Secret are correct, and check your app scopes
- **Playlist not found**: Make sure you're using the correct account credentials

## 📞 Need Help?

Check the main README.md file for detailed documentation and troubleshooting. 