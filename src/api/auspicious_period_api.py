import requests
import json
from datetime import datetime
import pytz

class AuspiciousPeriodAPI:
    def __init__(self):
        self.client_id = "efd2aa11-ce98-49e5-a04a-dfb5277d6856"
        self.client_secret = "0GMhVTymCt6t4eTO1ugpgiTc4ghIYXsfOfroZKKD"
        self.base_url = "https://api.prokerala.com/v2/astrology/auspicious-period"

    def get_access_token(self):
        token_url = "https://api.prokerala.com/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        try:
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            return token_data.get('access_token')
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None

    def get_auspicious_period(self, datetime_str=None, latitude="19.0821978", longitude="72.7411014", 
                              timezone_str="Asia/Kolkata", ayanamsa=1, language="en"):
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Failed to get access token"}

        if not datetime_str:
            tz = pytz.timezone(timezone_str)
            datetime_str = datetime.now(tz).isoformat()

        coordinates = f"{latitude},{longitude}"
        params = {
            'datetime': datetime_str,
            'coordinates': coordinates,
            'ayanamsa': str(ayanamsa),
            'timezone': timezone_str,
            'la': language
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            return {"success": True, "data": result}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                return {"error": "ERROR: Rate limit exceeded. Throttle your requests."}
            elif e.response.status_code == 402:
                return {"error": "ERROR: You have exceeded your quota allocation for the day"}
            elif e.response.status_code == 401:
                return {"error": f"Authentication error: {e.response.text}"}
            else:
                return {"error": f"API Request Failed with error {e}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {e}"}

if __name__ == "__main__":
    api = AuspiciousPeriodAPI()
    result = api.get_auspicious_period()
    print("Auspicious Period API Result:")
    print(json.dumps(result, indent=2, default=str)) 