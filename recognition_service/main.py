"""
Recognition Service - Main Entry Point

Multi-camera recognition service for companies.
Automatically discovers and processes all cameras for a company.
"""

import sys
import argparse
from .multi_camera_manager import MultiCameraManager
from .logging_config import setup_logging, get_logger

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Recognition Service - Multi-Camera Face Recognition'
    )
    
    parser.add_argument(
        '--company-slug',
        type=str,
        required=True,
        help='Company slug to process cameras for'
    )
    
    parser.add_argument(
        '--backend-url',
        type=str,
        required=True,
        help='Backend API URL'
    )
    
    parser.add_argument(
        '--refresh-interval',
        type=int,
        default=60,
        help='Interval to refresh camera list (seconds, default: 60)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    setup_logging('main', args.debug)
    logger = get_logger(__name__)
    
    logger.info('=' * 60)
    logger.info('Recognition Service - Multi-Camera Mode')
    logger.info('=' * 60)
    logger.info(f'Company: {args.company_slug}')
    logger.info(f'Backend: {args.backend_url}')
    logger.info(f'Refresh interval: {args.refresh_interval}s')
    logger.info('=' * 60)
    
    try:
        manager = MultiCameraManager(
            company_slug=args.company_slug,
            backend_url=args.backend_url,
            refresh_interval=args.refresh_interval
        )
        
        manager.run()
        
    except KeyboardInterrupt:
        logger.info('Received keyboard interrupt, shutting down...')
        sys.exit(0)
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
