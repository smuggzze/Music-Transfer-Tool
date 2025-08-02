from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
import requests
from dotenv import load_dotenv
from music_transfer import MusicTransferTool

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the music transfer tool
transfer_tool = MusicTransferTool()

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Get list of supported platforms"""
    platforms = transfer_tool.get_supported_platforms()
    return jsonify(platforms)

@app.route('/api/playlists', methods=['POST'])
def get_playlists():
    """Get playlists from a specific platform"""
    try:
        data = request.get_json()
        platform = data.get('platform')
        credentials = data.get('credentials', {})
        
        if not platform:
            return jsonify({'error': 'Platform is required'}), 400
        
        playlists = transfer_tool.get_playlists(platform, credentials)
        return jsonify({'playlists': playlists})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transfer', methods=['POST'])
def transfer_playlist():
    """Transfer a playlist from source to destination platform"""
    try:
        data = request.get_json()
        source_platform = data.get('source_platform')
        destination_platform = data.get('destination_platform')
        playlist_id = data.get('playlist_id')
        source_credentials = data.get('source_credentials', {})
        destination_credentials = data.get('destination_credentials', {})
        
        if not all([source_platform, destination_platform, playlist_id]):
            return jsonify({'error': 'Source platform, destination platform, and playlist ID are required'}), 400
        
        result = transfer_tool.transfer_playlist(
            source_platform=source_platform,
            destination_platform=destination_platform,
            playlist_id=playlist_id,
            source_credentials=source_credentials,
            destination_credentials=destination_credentials
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def get_transfer_status(task_id):
    """Get the status of a transfer task"""
    try:
        status = transfer_tool.get_transfer_status(task_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 