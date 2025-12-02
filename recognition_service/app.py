"""
Flask application for HTTP API.

Provides:
- GET /video_feed: MJPEG video stream
- GET /health: Service health check
"""

from flask import Flask, Response, jsonify
from flask_cors import CORS
from .config import Config
from . import streaming
from .logging_config import get_logger

logger = get_logger(__name__)


def create_app(config: Config) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config: Service configuration
    
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/video_feed')
    def video_feed():
        """Stream MJPEG video feed."""
        return Response(
            streaming.generate_mjpeg_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'ok',
            'streaming': streaming.is_streaming(),
            'cameraId': config.camera_id,
            'service': config.service_name,
        })
    
    return app








