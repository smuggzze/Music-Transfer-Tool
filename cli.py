#!/usr/bin/env python3
"""
Command Line Interface for Music Transfer Tool
"""

import argparse
import json
import sys
from music_transfer import MusicTransferTool
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description='Transfer playlists between music platforms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List supported platforms
  python cli.py platforms

  # List playlists from Spotify
  python cli.py playlists --platform spotify --client-id YOUR_ID --client-secret YOUR_SECRET

  # Transfer a playlist
  python cli.py transfer --source spotify --dest youtube_music --playlist-id PLAYLIST_ID
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Platforms command
    platforms_parser = subparsers.add_parser('platforms', help='List supported platforms')
    
    # Playlists command
    playlists_parser = subparsers.add_parser('playlists', help='List playlists from a platform')
    playlists_parser.add_argument('--platform', required=True, help='Platform to get playlists from')
    playlists_parser.add_argument('--client-id', help='Client ID (for Spotify)')
    playlists_parser.add_argument('--client-secret', help='Client Secret (for Spotify)')
    playlists_parser.add_argument('--redirect-uri', help='Redirect URI (for Spotify)')
    
    # Transfer command
    transfer_parser = subparsers.add_parser('transfer', help='Transfer a playlist')
    transfer_parser.add_argument('--source', required=True, help='Source platform')
    transfer_parser.add_argument('--dest', required=True, help='Destination platform')
    transfer_parser.add_argument('--playlist-id', required=True, help='Playlist ID to transfer')
    transfer_parser.add_argument('--source-client-id', help='Source platform client ID')
    transfer_parser.add_argument('--source-client-secret', help='Source platform client secret')
    transfer_parser.add_argument('--dest-client-id', help='Destination platform client ID')
    transfer_parser.add_argument('--dest-client-secret', help='Destination platform client secret')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    transfer_tool = MusicTransferTool()
    
    try:
        if args.command == 'platforms':
            platforms = transfer_tool.get_supported_platforms()
            print("Supported Platforms:")
            print("=" * 50)
            for platform in platforms:
                print(f"• {platform['name']} ({platform['id']})")
                print(f"  {platform['description']}")
                if platform['requires_auth']:
                    print(f"  Requires authentication: {', '.join(platform['auth_fields'])}")
                print()
        
        elif args.command == 'playlists':
            credentials = {}
            if args.client_id:
                credentials['client_id'] = args.client_id
            if args.client_secret:
                credentials['client_secret'] = args.client_secret
            if args.redirect_uri:
                credentials['redirect_uri'] = args.redirect_uri
            
            playlists = transfer_tool.get_playlists(args.platform, credentials)
            print(f"Playlists from {args.platform}:")
            print("=" * 50)
            for playlist in playlists:
                print(f"• {playlist['name']} (ID: {playlist['id']})")
                print(f"  Tracks: {playlist['track_count']}")
                print(f"  Owner: {playlist['owner']}")
                if playlist.get('description'):
                    print(f"  Description: {playlist['description']}")
                print()
        
        elif args.command == 'transfer':
            source_credentials = {}
            dest_credentials = {}
            
            if args.source_client_id:
                source_credentials['client_id'] = args.source_client_id
            if args.source_client_secret:
                source_credentials['client_secret'] = args.source_client_secret
            if args.dest_client_id:
                dest_credentials['client_id'] = args.dest_client_id
            if args.dest_client_secret:
                dest_credentials['client_secret'] = args.dest_client_secret
            
            print(f"Starting transfer from {args.source} to {args.dest}...")
            result = transfer_tool.transfer_playlist(
                source_platform=args.source,
                destination_platform=args.dest,
                playlist_id=args.playlist_id,
                source_credentials=source_credentials,
                destination_credentials=dest_credentials
            )
            
            print(f"Transfer started! Task ID: {result['task_id']}")
            print("Monitoring progress...")
            
            # Monitor progress
            import time
            while True:
                status = transfer_tool.get_transfer_status(result['task_id'])
                if status.get('error'):
                    print(f"Error: {status['error']}")
                    break
                
                print(f"\rProgress: {status['progress']}% - {status['message']}", end='', flush=True)
                
                if status['status'] in ['completed', 'failed']:
                    print(f"\nTransfer {status['status']}: {status['message']}")
                    break
                
                time.sleep(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 