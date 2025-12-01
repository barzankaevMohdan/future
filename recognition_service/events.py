"""
Event sending module.

Sends presence events (IN/OUT) to backend API.
"""

import requests
from typing import Literal
from .config import Config
from .logging_config import get_logger

logger = get_logger(__name__)

EventType = Literal['IN', 'OUT']


def send_event(employee_id: int, event_type: EventType, config: Config) -> bool:
    """
    Send presence event to backend.
    
    Args:
        employee_id: Employee ID
        event_type: Event type ('IN' or 'OUT')
        config: Service configuration
    
    Returns:
        True if event sent successfully
    """
    url = f'{config.backend_url}/api/events'
    
    payload = {
        'employeeId': employee_id,
        'type': event_type,
    }
    
    try:
        logger.info(f'📤 Sending event {event_type} for employee {employee_id}')
        
        response = requests.post(url, json=payload, timeout=5)
        
        if response.ok:
            logger.info(f'✅ Event sent successfully')
            return True
        else:
            logger.error(f'❌ Failed to send event: {response.status_code} {response.text}')
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f'❌ Timeout sending event to {url}')
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f'❌ Connection error sending event to {url}')
        return False
    except Exception as e:
        logger.error(f'❌ Error sending event: {e}')
        return False







