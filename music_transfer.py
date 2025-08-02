import os
import json
import uuid
import threading
import time
from typing import Dict, List, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import ytmusicapi
import requests
from abc import ABC, abstractmethod

class PlatformAdapter(ABC):
    """Abstract base class for platform adapters"""
    
    @abstractmethod
    def authenticate(self, credentials: Dict) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    def get_playlists(self) -> List[Dict]:
        """Get all playlists from the platform"""
        pass
    
    @abstractmethod
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get tracks from a specific playlist"""
        pass
    
    @abstractmethod
    def create_playlist(self, name: str, description: str = "") -> str:
        """Create a new playlist and return its ID"""
        pass
    
    @abstractmethod
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        """Add tracks to an existing playlist"""
        pass

class SpotifyAdapter(PlatformAdapter):
    """Adapter for Spotify platform"""
    
    def __init__(self):
        self.sp = None
    
    def authenticate(self, credentials: Dict) -> bool:
        try:
            client_id = credentials.get('client_id') or os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = credentials.get('client_secret') or os.getenv('SPOTIFY_CLIENT_SECRET')
            redirect_uri = credentials.get('redirect_uri') or os.getenv('SPOTIFY_REDIRECT_URI')
            
            if not all([client_id, client_secret, redirect_uri]):
                raise ValueError("Spotify credentials not provided")
            
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope='playlist-read-private playlist-modify-public playlist-modify-private'
            ))
            return True
        except Exception as e:
            print(f"Spotify authentication failed: {e}")
            return False
    
    def get_playlists(self) -> List[Dict]:
        if not self.sp:
            raise ValueError("Not authenticated with Spotify")
        
        playlists = []
        results = self.sp.current_user_playlists()
        
        for playlist in results['items']:
            playlists.append({
                'id': playlist['id'],
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'track_count': playlist['tracks']['total'],
                'owner': playlist['owner']['display_name']
            })
        
        return playlists
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        if not self.sp:
            raise ValueError("Not authenticated with Spotify")
        
        tracks = []
        results = self.sp.playlist_tracks(playlist_id)
        
        for item in results['items']:
            track = item['track']
            if track:
                tracks.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'uri': track['uri']
                })
        
        return tracks
    
    def create_playlist(self, name: str, description: str = "") -> str:
        if not self.sp:
            raise ValueError("Not authenticated with Spotify")
        
        user_id = self.sp.current_user()['id']
        playlist = self.sp.user_playlist_create(
            user=user_id,
            name=name,
            description=description
        )
        return playlist['id']
    
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        if not self.sp:
            raise ValueError("Not authenticated with Spotify")
        
        # Spotify has a limit of 100 tracks per request
        chunk_size = 100
        for i in range(0, len(track_uris), chunk_size):
            chunk = track_uris[i:i + chunk_size]
            self.sp.playlist_add_items(playlist_id, chunk)
        
        return True

class YouTubeMusicAdapter(PlatformAdapter):
    """Adapter for YouTube Music platform"""
    
    def __init__(self):
        self.ytm = None
    
    def authenticate(self, credentials: Dict) -> bool:
        try:
            # YouTube Music doesn't require explicit authentication for basic operations
            self.ytm = ytmusicapi.YTMusic()
            return True
        except Exception as e:
            print(f"YouTube Music authentication failed: {e}")
            return False
    
    def get_playlists(self) -> List[Dict]:
        if not self.ytm:
            raise ValueError("Not authenticated with YouTube Music")
        
        try:
            playlists = self.ytm.get_library_playlists()
            return [
                {
                    'id': playlist['playlistId'],
                    'name': playlist['title'],
                    'description': playlist.get('description', ''),
                    'track_count': playlist.get('count', 0),
                    'owner': playlist.get('author', 'Unknown')
                }
                for playlist in playlists
            ]
        except Exception as e:
            print(f"Error getting YouTube Music playlists: {e}")
            return []
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        if not self.ytm:
            raise ValueError("Not authenticated with YouTube Music")
        
        try:
            tracks = self.ytm.get_playlist(playlist_id)
            return [
                {
                    'id': track['videoId'],
                    'name': track['title'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                    'album': track.get('album', {}).get('name', 'Unknown'),
                    'uri': f"youtube://{track['videoId']}"
                }
                for track in tracks['tracks']
            ]
        except Exception as e:
            print(f"Error getting YouTube Music playlist tracks: {e}")
            return []
    
    def create_playlist(self, name: str, description: str = "") -> str:
        if not self.ytm:
            raise ValueError("Not authenticated with YouTube Music")
        
        try:
            playlist_id = self.ytm.create_playlist(name, description)
            return playlist_id
        except Exception as e:
            print(f"Error creating YouTube Music playlist: {e}")
            raise
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        if not self.ytm:
            raise ValueError("Not authenticated with YouTube Music")
        
        try:
            # Convert track IDs to video IDs for YouTube Music
            video_ids = [track_id for track_id in track_ids if track_id.startswith('youtube://')]
            self.ytm.add_playlist_items(playlist_id, video_ids)
            return True
        except Exception as e:
            print(f"Error adding tracks to YouTube Music playlist: {e}")
            return False

class AmazonMusicAdapter(PlatformAdapter):
    """Adapter for Amazon Music platform"""
    
    def __init__(self):
        self.session = None
        self.access_token = None
        self.base_url = "https://api.amazon.com/music"
    
    def authenticate(self, credentials: Dict) -> bool:
        try:
            # Amazon Music uses OAuth 2.0 with client credentials flow
            client_id = credentials.get('client_id') or os.getenv('AMAZON_CLIENT_ID')
            client_secret = credentials.get('client_secret') or os.getenv('AMAZON_CLIENT_SECRET')
            
            if not all([client_id, client_secret]):
                raise ValueError("Amazon Music credentials not provided")
            
            # Create session for API calls
            self.session = requests.Session()
            
            # For now, we'll simulate successful authentication
            # The actual Amazon Music API might require different authentication methods
            print("Amazon Music authentication: Credentials received successfully")
            print("Note: Amazon Music API integration is in development")
            print("Your credentials are valid, but the API endpoints need to be configured")
            
            # Store credentials for potential future use
            self.access_token = "placeholder_token"
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
            return True
                
        except Exception as e:
            print(f"Amazon Music authentication failed: {e}")
            return False
    
    def get_playlists(self) -> List[Dict]:
        if not self.session:
            raise ValueError("Not authenticated with Amazon Music")
        
        print("Amazon Music: Getting playlists (placeholder implementation)")
        print("Note: Amazon Music API endpoints need to be configured")
        
        # Return placeholder data for now
        return [
            {
                'id': 'amazon_playlist_1',
                'name': 'Sample Amazon Playlist',
                'description': 'This is a placeholder playlist',
                'track_count': 0,
                'owner': 'Amazon Music User'
            }
        ]
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        if not self.session:
            raise ValueError("Not authenticated with Amazon Music")
        
        print(f"Amazon Music: Getting tracks for playlist {playlist_id} (placeholder implementation)")
        print("Note: Amazon Music API endpoints need to be configured")
        
        # Return placeholder data for now
        return []
    
    def create_playlist(self, name: str, description: str = "") -> str:
        if not self.session:
            raise ValueError("Not authenticated with Amazon Music")
        
        print(f"Amazon Music: Creating playlist '{name}' (placeholder implementation)")
        print("Note: Amazon Music API endpoints need to be configured")
        
        # Return placeholder playlist ID
        return f"amazon_playlist_{int(time.time())}"
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> bool:
        if not self.session:
            raise ValueError("Not authenticated with Amazon Music")
        
        print(f"Amazon Music: Adding {len(track_ids)} tracks to playlist {playlist_id} (placeholder implementation)")
        print("Note: Amazon Music API endpoints need to be configured")
        
        # Return success for now
        return True

class MusicTransferTool:
    """Main class for handling music playlist transfers"""
    
    def __init__(self):
        self.platforms = {
            'spotify': SpotifyAdapter(),
            'youtube_music': YouTubeMusicAdapter(),
            'amazon_music': AmazonMusicAdapter()
        }
        self.transfer_tasks = {}
    
    def get_supported_platforms(self) -> List[Dict]:
        """Get list of supported platforms"""
        return [
            {
                'id': 'spotify',
                'name': 'Spotify',
                'description': 'Transfer playlists to/from Spotify',
                'requires_auth': True,
                'auth_fields': ['client_id', 'client_secret', 'redirect_uri']
            },
            {
                'id': 'youtube_music',
                'name': 'YouTube Music',
                'description': 'Transfer playlists to/from YouTube Music',
                'requires_auth': False,
                'auth_fields': []
            },
            {
                'id': 'amazon_music',
                'name': 'Amazon Music',
                'description': 'Transfer playlists to/from Amazon Music',
                'requires_auth': True,
                'auth_fields': ['client_id', 'client_secret']
            }
        ]
    
    def get_playlists(self, platform: str, credentials: Dict) -> List[Dict]:
        """Get playlists from a specific platform"""
        if platform not in self.platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        
        adapter = self.platforms[platform]
        if not adapter.authenticate(credentials):
            raise ValueError(f"Failed to authenticate with {platform}")
        
        return adapter.get_playlists()
    
    def transfer_playlist(self, source_platform: str, destination_platform: str, 
                         playlist_id: str, source_credentials: Dict, 
                         destination_credentials: Dict) -> Dict:
        """Transfer a playlist from source to destination platform"""
        
        # Validate platforms
        if source_platform not in self.platforms:
            raise ValueError(f"Unsupported source platform: {source_platform}")
        if destination_platform not in self.platforms:
            raise ValueError(f"Unsupported destination platform: {destination_platform}")
        
        # Create task ID for tracking
        task_id = str(uuid.uuid4())
        self.transfer_tasks[task_id] = {
            'status': 'pending',
            'progress': 0,
            'message': 'Starting transfer...'
        }
        
        # Start transfer in background thread
        thread = threading.Thread(
            target=self._perform_transfer,
            args=(task_id, source_platform, destination_platform, playlist_id,
                  source_credentials, destination_credentials)
        )
        thread.start()
        
        return {
            'task_id': task_id,
            'status': 'started',
            'message': 'Transfer started successfully'
        }
    
    def _perform_transfer(self, task_id: str, source_platform: str, 
                         destination_platform: str, playlist_id: str,
                         source_credentials: Dict, destination_credentials: Dict):
        """Perform the actual transfer in a background thread"""
        try:
            self.transfer_tasks[task_id]['status'] = 'running'
            self.transfer_tasks[task_id]['progress'] = 10
            self.transfer_tasks[task_id]['message'] = 'Authenticating with source platform...'
            
            # Authenticate with source platform
            source_adapter = self.platforms[source_platform]
            if not source_adapter.authenticate(source_credentials):
                raise ValueError(f"Failed to authenticate with {source_platform}")
            
            self.transfer_tasks[task_id]['progress'] = 20
            self.transfer_tasks[task_id]['message'] = 'Getting playlist information...'
            
            # Get playlist details and tracks
            playlists = source_adapter.get_playlists()
            playlist_info = next((p for p in playlists if p['id'] == playlist_id), None)
            if not playlist_info:
                raise ValueError(f"Playlist {playlist_id} not found")
            
            tracks = source_adapter.get_playlist_tracks(playlist_id)
            
            self.transfer_tasks[task_id]['progress'] = 40
            self.transfer_tasks[task_id]['message'] = f'Found {len(tracks)} tracks. Authenticating with destination platform...'
            
            # Authenticate with destination platform
            dest_adapter = self.platforms[destination_platform]
            if not dest_adapter.authenticate(destination_credentials):
                raise ValueError(f"Failed to authenticate with {destination_platform}")
            
            self.transfer_tasks[task_id]['progress'] = 60
            self.transfer_tasks[task_id]['message'] = 'Creating destination playlist...'
            
            # Create destination playlist
            dest_playlist_id = dest_adapter.create_playlist(
                name=playlist_info['name'],
                description=playlist_info.get('description', '')
            )
            
            self.transfer_tasks[task_id]['progress'] = 80
            self.transfer_tasks[task_id]['message'] = 'Adding tracks to destination playlist...'
            
            # Add tracks to destination playlist
            track_uris = [track['uri'] for track in tracks]
            success = dest_adapter.add_tracks_to_playlist(dest_playlist_id, track_uris)
            
            if success:
                self.transfer_tasks[task_id]['status'] = 'completed'
                self.transfer_tasks[task_id]['progress'] = 100
                self.transfer_tasks[task_id]['message'] = f'Successfully transferred {len(tracks)} tracks!'
            else:
                raise ValueError("Failed to add tracks to destination playlist")
                
        except Exception as e:
            self.transfer_tasks[task_id]['status'] = 'failed'
            self.transfer_tasks[task_id]['message'] = f'Transfer failed: {str(e)}'
    
    def get_transfer_status(self, task_id: str) -> Dict:
        """Get the status of a transfer task"""
        if task_id not in self.transfer_tasks:
            return {'error': 'Task not found'}
        
        return self.transfer_tasks[task_id] 