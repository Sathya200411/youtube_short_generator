import requests
import json
from datetime import datetime
import pytz

def get_access_token():
    """Get access token using client credentials"""
    client_id = "efd2aa11-ce98-49e5-a04a-dfb5277d6856"
    client_secret = "0GMhVTymCt6t4eTO1ugpgiTc4ghIYXsfOfroZKKD"
    
    token_url = "https://api.prokerala.com/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    try:
        response = requests.post(token_url, data=data, timeout=30)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        return None

def make_api_call(endpoint, access_token):
    """Make API call and return raw response"""
    tz = pytz.timezone("Asia/Kolkata")
    datetime_str = datetime.now(tz).isoformat()
    
    coordinates = "19.0821978,72.7411014"
    params = {
        'datetime': datetime_str,
        'coordinates': coordinates,
        'ayanamsa': '1',
        'timezone': 'Asia/Kolkata',
        'la': 'en'
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(f"https://api.prokerala.com/v2/astrology/{endpoint}", 
                              headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("=== Debug API Responses ===")
    
    # Get access token
    token = get_access_token()
    if not token:
        print("Failed to get access token")
        exit(1)
    
    print(f"Token: {token[:20]}...")
    
    # Test each API endpoint
    endpoints = ["panchang", "auspicious-period", "inauspicious-period"]
    
    for endpoint in endpoints:
        print(f"\n=== {endpoint.upper()} API Response ===")
        result = make_api_call(endpoint, token)
        print(json.dumps(result, indent=2, default=str))
        print(f"\n{'='*50}") 