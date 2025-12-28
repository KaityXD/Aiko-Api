import base64
import json
import sys

def get_super_properties():
    """Generates a valid X-Super-Properties header value."""
    properties = {
        "os": sys.platform,
        "browser": "Chrome",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "browser_version": "91.0.4472.124",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": 100000, # This should ideally be dynamic or updated frequently
        "client_event_source": None
    }
    
    return base64.b64encode(json.dumps(properties).encode()).decode('utf-8')

def get_user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
