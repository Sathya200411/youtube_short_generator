import requests
import json
from datetime import datetime
import pytz

class EnglishAstrologyAPI:
    def __init__(self):
        # Load credentials from cred.text
        self.client_id = "efd2aa11-ce98-49e5-a04a-dfb5277d6856"
        self.client_secret = "0GMhVTymCt6t4eTO1ugpgiTc4ghIYXsfOfroZKKD"
        self.base_url = "https://api.prokerala.com/v2/astrology"
        
    def get_access_token(self):
        """Get access token using client credentials"""
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

    def _make_api_call(self, endpoint, datetime_str=None, latitude="19.0821978", longitude="72.7411014", 
                       timezone_str="Asia/Kolkata", ayanamsa=1, language="en"):
        """Generic method to make API calls"""
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
            response = requests.get(f"{self.base_url}/{endpoint}", headers=headers, params=params, timeout=30)
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

    def get_panchang(self, datetime_str=None, latitude="19.0821978", longitude="72.7411014", 
                     timezone_str="Asia/Kolkata", ayanamsa=1, language="en"):
        """Get panchang data (basic astrological elements)"""
        return self._make_api_call("panchang", datetime_str, latitude, longitude, timezone_str, ayanamsa, language)

    def get_auspicious_period(self, datetime_str=None, latitude="19.0821978", longitude="72.7411014", 
                              timezone_str="Asia/Kolkata", ayanamsa=1, language="en"):
        """Get auspicious periods (muhurat)"""
        return self._make_api_call("auspicious-period", datetime_str, latitude, longitude, timezone_str, ayanamsa, language)

    def get_inauspicious_period(self, datetime_str=None, latitude="19.0821978", longitude="72.7411014", 
                                timezone_str="Asia/Kolkata", ayanamsa=1, language="en"):
        """Get inauspicious periods (avoid these times)"""
        return self._make_api_call("inauspicious-period", datetime_str, latitude, longitude, timezone_str, ayanamsa, language)

    def get_ritu(self, datetime_str=None, latitude="19.0821978", longitude="72.7411014", 
                 timezone_str="Asia/Kolkata", ayanamsa=1, language="en"):
        """Get ritu (season) information"""
        return self._make_api_call("ritu", datetime_str, latitude, longitude, timezone_str, ayanamsa, language)

    def get_all_data(self, datetime_str=None, latitude="19.0821978", longitude="72.7411014", 
                     timezone_str="Asia/Kolkata", ayanamsa=1, language="en"):
        """Get all astrology data in one call"""
        results = {}
        
        # Get all data
        results['panchang'] = self.get_panchang(datetime_str, latitude, longitude, timezone_str, ayanamsa, language)
        results['auspicious_period'] = self.get_auspicious_period(datetime_str, latitude, longitude, timezone_str, ayanamsa, language)
        results['inauspicious_period'] = self.get_inauspicious_period(datetime_str, latitude, longitude, timezone_str, ayanamsa, language)
        results['ritu'] = self.get_ritu(datetime_str, latitude, longitude, timezone_str, ayanamsa, language)
        
        return results

    def save_to_file(self, data, filename=None):
        """Save API results to a JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"english_astrology_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

# Example usage
if __name__ == "__main__":
    api = EnglishAstrologyAPI()
    
    print("=== English Astrology API Client ===")
    print("Fetching all astrology data...")
    
    # Get all data
    all_data = api.get_all_data()
    
    # Print results
    print("\n=== Results ===")
    for api_name, result in all_data.items():
        print(f"\n{api_name.upper().replace('_', ' ')}:")
        if result.get('success'):
            print("✅ Success")
            if 'data' in result['data']:
                print(f"Status: {result['data']['status']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    # Save to file
    api.save_to_file(all_data)
    
    print("\n=== Individual API Tests ===")
    
    # Test individual APIs
    print("\n1. Panchang:")
    panchang_result = api.get_panchang()
    print(json.dumps(panchang_result, indent=2, default=str)[:500] + "...")
    
    print("\n2. Auspicious Period:")
    auspicious_result = api.get_auspicious_period()
    print(json.dumps(auspicious_result, indent=2, default=str)[:500] + "...")
    
    print("\n3. Inauspicious Period:")
    inauspicious_result = api.get_inauspicious_period()
    print(json.dumps(inauspicious_result, indent=2, default=str)[:500] + "...")
    
    print("\n4. Ritu (Season):")
    ritu_result = api.get_ritu()
    print(json.dumps(ritu_result, indent=2, default=str)[:500] + "...") 