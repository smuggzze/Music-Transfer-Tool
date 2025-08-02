# Music Transfer Tool

A powerful web application that allows you to transfer playlists between different music platforms seamlessly. Transfer your playlists from Spotify to YouTube Music, or between any supported platforms, regardless of playlist size.

## Features

- **Multi-Platform Support**: Transfer between Spotify, YouTube Music, Amazon Music, and more
- **Large Playlist Support**: Handle playlists of any size with background processing
- **Real-time Progress**: Track transfer progress with live updates
- **Modern Web Interface**: Beautiful, responsive UI built with Tailwind CSS
- **Secure Authentication**: Secure credential handling for platform APIs
- **Background Processing**: Non-blocking transfers that don't freeze the interface
- **Transfer History**: Keep track of your recent transfers

## Supported Platforms

### Currently Supported
- **Spotify** - Full playlist import/export support
- **YouTube Music** - Full playlist import/export support
- **Amazon Music** - Full playlist import/export support

### Coming Soon
- Apple Music
- Deezer
- Tidal

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Web browser

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Music-Transfer-Tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   Create a `.env` file in the project root:
   ```env
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:5000/callback
   AMAZON_CLIENT_ID=your_amazon_client_id
   AMAZON_CLIENT_SECRET=your_amazon_client_secret
   ```

## Setup Instructions

### Spotify Setup

1. **Create a Spotify App**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Click "Create App"
   - Fill in the app details
   - Add `http://localhost:5000/callback` to Redirect URIs

2. **Get Your Credentials**
   - Copy your Client ID and Client Secret
   - Add them to your `.env` file or enter them in the web interface

### Amazon Music Setup

1. **Create an Amazon Developer Account**
   - Go to [Amazon Developer Console](https://developer.amazon.com/)
   - Sign in with your Amazon account
   - Create a new security profile

2. **Set up Amazon Music API**
   - Navigate to the Amazon Music API section
   - Create a new app for Amazon Music
   - Configure OAuth 2.0 settings
   - Add the required scopes: `music:playlist_read` and `music:playlist_write`

3. **Get Your Credentials**
   - Copy your Client ID and Client Secret
   - Add them to your `.env` file or enter them in the web interface

### YouTube Music Setup

YouTube Music doesn't require explicit API credentials for basic operations, but you may need to authenticate through the web interface.

## Running the Application

1. **Start the server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

3. **Start transferring playlists!**
   - Select your source platform
   - Choose your destination platform
   - Select the playlist you want to transfer
   - Click "Start Transfer"

## Usage Guide

### Basic Transfer

1. **Select Source Platform**
   - Choose the platform where your playlist currently exists
   - Enter credentials if required (Spotify and Amazon Music need API credentials)

2. **Load Playlists**
   - The app will automatically load your playlists
   - Select the playlist you want to transfer

3. **Select Destination Platform**
   - Choose where you want to transfer the playlist to
   - Enter credentials if required

4. **Start Transfer**
   - Click "Start Transfer" to begin the process
   - Monitor progress in real-time
   - View transfer history below

### Advanced Features

- **Large Playlists**: The tool handles playlists of any size by processing them in chunks
- **Background Processing**: Transfers run in the background, so you can continue using the app
- **Progress Tracking**: Real-time progress updates with detailed status messages
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Security

- Credentials are handled securely and not stored permanently
- All API calls use HTTPS
- No sensitive data is logged or stored
- Environment variables are used for sensitive configuration

## 🛠️ Development

### Project Structure
```
Music-Transfer-Tool/
├── app.py                 # Main Flask application
├── music_transfer.py      # Core transfer logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

### Adding New Platforms

To add support for a new platform:

1. **Create a new adapter class** in `music_transfer.py`
   ```python
   class NewPlatformAdapter(PlatformAdapter):
       def authenticate(self, credentials: Dict) -> bool:
           # Implement authentication
           pass
       
       def get_playlists(self) -> List[Dict]:
           # Implement playlist retrieval
           pass
       
       # ... implement other required methods
   ```

2. **Register the platform** in the `MusicTransferTool` class
   ```python
   self.platforms = {
       'spotify': SpotifyAdapter(),
       'youtube_music': YouTubeMusicAdapter(),
       'amazon_music': AmazonMusicAdapter(),
       'new_platform': NewPlatformAdapter()  # Add here
   }
   ```

3. **Update the supported platforms list**
   ```python
   def get_supported_platforms(self) -> List[Dict]:
       return [
           # ... existing platforms
           {
               'id': 'new_platform',
               'name': 'New Platform',
               'description': 'Transfer playlists to/from New Platform',
               'requires_auth': True,
               'auth_fields': ['api_key', 'secret']
           }
       ]
   ```

## Troubleshooting

### Common Issues

1. **Spotify Authentication Failed**
   - Verify your Client ID and Client Secret are correct
   - Ensure your redirect URI matches exactly
   - Check that your Spotify app has the correct permissions

2. **Amazon Music Authentication Failed**
   - Verify your Client ID and Client Secret are correct
   - Ensure your app has the correct scopes configured
   - Check that your Amazon Developer account is properly set up

3. **Playlist Not Found**
   - Make sure you're logged into the correct account
   - Verify the playlist is accessible (not private if using a different account)

4. **Transfer Fails**
   - Check your internet connection
   - Verify both platform credentials are correct
   - Ensure the destination platform supports the source tracks

### Debug Mode

Run the application in debug mode for more detailed error messages:
```bash
export FLASK_ENV=development
python app.py
```

## API Documentation

### Endpoints

- `GET /api/platforms` - Get list of supported platforms
- `POST /api/playlists` - Get playlists from a platform
- `POST /api/transfer` - Start a playlist transfer
- `GET /api/status/<task_id>` - Get transfer status

### Example API Usage

```bash
# Get supported platforms
curl http://localhost:5000/api/platforms

# Get playlists from Spotify
curl -X POST http://localhost:5000/api/playlists \
  -H "Content-Type: application/json" \
  -d '{"platform": "spotify", "credentials": {"client_id": "..."}}'

# Start a transfer
curl -X POST http://localhost:5000/api/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "source_platform": "spotify",
    "destination_platform": "amazon_music",
    "playlist_id": "playlist_id_here",
    "source_credentials": {...},
    "destination_credentials": {...}
  }'
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Spotipy](https://spotipy.readthedocs.io/) - Spotify Web API wrapper
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - YouTube Music API wrapper
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework

## Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed information about your problem

---

**Happy transferring!**
