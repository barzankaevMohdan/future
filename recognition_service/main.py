"""
Recognition Service - Main Entry Point

Initializes InsightFace and starts video processing loop.
"""

import sys
import argparse
from insightface.app import FaceAnalysis
from .config import load_config, Config
from .logging_config import setup_logging, get_logger
from . import video_loop

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Recognition Service - Face Recognition and Presence Tracking'
    )
    
    parser.add_argument(
        '--camera-id',
        type=str,
        help='Camera identifier (overrides CAMERA_ID env)'
    )
    
    parser.add_argument(
        '--camera-source',
        type=str,
        help='Camera source (overrides CAMERA_SOURCE env)'
    )
    
    parser.add_argument(
        '--backend-url',
        type=str,
        help='Backend URL (overrides BACKEND_URL env)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()


def apply_cli_overrides(config: Config, args: argparse.Namespace) -> Config:
    """
    Apply CLI argument overrides to config.
    
    Args:
        config: Base configuration
        args: Parsed CLI arguments
    
    Returns:
        Updated configuration
    """
    overrides = {}
    
    if args.camera_id:
        overrides['camera_id'] = args.camera_id
    
    if args.camera_source:
        overrides['camera_source'] = args.camera_source
    
    if args.backend_url:
        overrides['backend_url'] = args.backend_url
    
    if args.debug:
        overrides['debug_mode'] = True
    
    if not overrides:
        return config
    
    # Create new config with overrides
    config_dict = config.__dict__.copy()
    config_dict.update(overrides)
    
    return Config(**config_dict)


def initialize_insightface(config: Config) -> FaceAnalysis:
    """
    Initialize InsightFace FaceAnalysis.
    
    Args:
        config: Service configuration
    
    Returns:
        Initialized FaceAnalysis instance
    """
    logger.info('Initializing InsightFace AI...')
    
    face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
    face_app.prepare(ctx_id=0, det_size=config.insightface_det_size)
    
    logger.info(f'✅ InsightFace initialized (det_size={config.insightface_det_size})')
    
    return face_app


def print_banner(config: Config) -> None:
    """
    Print startup banner with configuration.
    
    Args:
        config: Service configuration
    """
    logger.info('=' * 60)
    logger.info('Recognition Service - AI-Powered')
    logger.info('=' * 60)
    logger.info(f'Service: {config.service_name}')
    logger.info(f'Camera ID: {config.camera_id}')
    logger.info(f'Backend: {config.backend_url}')
    logger.info(f'Camera: {config.camera_source}')
    logger.info(f'Video port: {config.video_port}')
    logger.info(f'Preprocessing: {config.enable_preprocessing}')
    logger.info(f'Min face height: {config.min_face_height_pixels}px')
    logger.info(f'Min blur variance: {config.min_blur_variance}')
    logger.info(f'Embeddings per track: {config.min_embeddings_per_track}')
    logger.info(f'IN threshold: {config.in_threshold_seconds}s')
    logger.info(f'OUT threshold: {config.out_threshold_seconds}s')
    logger.info('=' * 60)


def main() -> None:
    """Main entry point."""
    global logger
    # Parse CLI arguments
    args = parse_args()
    
    # Load configuration
    config = load_config()
    
    # Apply CLI overrides
    config = apply_cli_overrides(config, args)
    
    # Setup logging
    setup_logging(config.camera_id, config.debug_mode)
    logger = get_logger(__name__)
    
    # Print banner
    print_banner(config)
    
    try:
        # Initialize InsightFace
        face_app = initialize_insightface(config)
        
        # Start video loop
        video_loop.run(face_app, config)
        
    except KeyboardInterrupt:
        logger.info('Received keyboard interrupt, shutting down...')
        sys.exit(0)
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()






