#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple web server for Telegram Web App
Serves the mini-app interface
"""
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Get the directory where this file is located
WEBAPP_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def index():
    """Serve the main Web App page"""
    return send_from_directory(WEBAPP_DIR, 'index.html')


@app.route('/webapp')
def webapp():
    """Alternative route for Web App"""
    return send_from_directory(WEBAPP_DIR, 'index.html')


@app.route('/api/status')
def api_status():
    """API endpoint for bot status"""
    return jsonify({
        'status': 'online',
        'bot': 'GuideFarm',
        'version': '1.0.0',
        'timestamp': os.popen('date +%s').read().strip()
    })


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    return jsonify({
        'guides_created': 0,
        'active_users': 1,
        'ai_model': 'Gemini 2.0 Flash',
        'uptime': '100%'
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Web App server on port {port}")
    print(f"Serving from: {WEBAPP_DIR}")
    print("DOBRO. Web App server ready.")
    app.run(host='0.0.0.0', port=port, debug=False)
