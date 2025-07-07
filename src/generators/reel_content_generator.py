import requests
import json
from datetime import datetime
import pytz

class ReelContentGenerator:
    def __init__(self):
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

    def _make_api_call(self, endpoint, datetime_str=None, latitude="17.3850", longitude="78.4867", 
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
            return {"error": f"API Request Failed with error {e}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {e}"}

    def get_formatted_content(self, datetime_str=None, latitude="17.3850", longitude="78.4867", 
                             timezone_str="Asia/Kolkata"):
        """Get formatted content for reels"""
        
        # Set default datetime to tomorrow if not provided
        if not datetime_str:
            tz = pytz.timezone(timezone_str)
            from datetime import timedelta
            tomorrow = datetime.now(tz) + timedelta(days=1)
            datetime_str = tomorrow.isoformat()
        
        # Get panchang data
        panchang_result = self._make_api_call("panchang", datetime_str, latitude, longitude, timezone_str)
        auspicious_result = self._make_api_call("auspicious-period", datetime_str, latitude, longitude, timezone_str)
        inauspicious_result = self._make_api_call("inauspicious-period", datetime_str, latitude, longitude, timezone_str)
        
        formatted_data = {}
        
        if panchang_result.get('success'):
            panchang_data = panchang_result['data']['data']
            
            # Extract date and day
            date_obj = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            formatted_data['year'] = date_obj.year
            formatted_data['day'] = date_obj.strftime('%A')  # Full day name
            formatted_data['date'] = date_obj.strftime('%d %B %Y')  # DD Month YYYY
            
            # Extract sunrise and sunset
            sunrise = panchang_data.get('sunrise', '')
            sunset = panchang_data.get('sunset', '')
            if sunrise:
                sunrise_time = datetime.fromisoformat(sunrise.replace('Z', '+00:00'))
                formatted_data['sunrise'] = sunrise_time.strftime('%I:%M %p')
            if sunset:
                sunset_time = datetime.fromisoformat(sunset.replace('Z', '+00:00'))
                formatted_data['sunset'] = sunset_time.strftime('%I:%M %p')
            
            # Extract current tithi
            tithi_list = panchang_data.get('tithi', [])
            if tithi_list:
                current_tithi = tithi_list[0]  # Current tithi
                formatted_data['tithi'] = {
                    'name': current_tithi.get('name', ''),
                    'paksha': current_tithi.get('paksha', '')
                }
            
            # Extract current nakshatra
            nakshatra_list = panchang_data.get('nakshatra', [])
            if nakshatra_list:
                current_nakshatra = nakshatra_list[0]  # Current nakshatra
                formatted_data['nakshatra'] = {
                    'name': current_nakshatra.get('name', ''),
                    'lord': current_nakshatra.get('lord', {}).get('name', '') if current_nakshatra.get('lord') else ''
                }
        
        # Extract auspicious periods
        if auspicious_result.get('success'):
            auspicious_data = auspicious_result['data']['data']
            formatted_data['auspicious_periods'] = []
            if 'muhurat' in auspicious_data:
                for period in auspicious_data['muhurat']:
                    period_info = {
                        'name': period.get('name', ''),
                        'type': period.get('type', ''),
                        'periods': []
                    }
                    for time_period in period.get('period', []):
                        start_time = datetime.fromisoformat(time_period['start'].replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(time_period['end'].replace('Z', '+00:00'))
                        period_info['periods'].append({
                            'start': start_time.strftime('%I:%M %p'),
                            'end': end_time.strftime('%I:%M %p')
                        })
                    formatted_data['auspicious_periods'].append(period_info)
        
        # Extract inauspicious periods
        if inauspicious_result.get('success'):
            inauspicious_data = inauspicious_result['data']['data']
            formatted_data['inauspicious_periods'] = []
            if 'muhurat' in inauspicious_data:
                for period in inauspicious_data['muhurat']:
                    period_info = {
                        'name': period.get('name', ''),
                        'type': period.get('type', ''),
                        'periods': []
                    }
                    for time_period in period.get('period', []):
                        start_time = datetime.fromisoformat(time_period['start'].replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(time_period['end'].replace('Z', '+00:00'))
                        period_info['periods'].append({
                            'start': start_time.strftime('%I:%M %p'),
                            'end': end_time.strftime('%I:%M %p')
                        })
                    formatted_data['inauspicious_periods'].append(period_info)
        
        return formatted_data

    def generate_reel_text(self, data):
        """Generate formatted text for reel overlays"""
        text_lines = []
        
        # Header
        text_lines.append(f"📅 {data['date']}")
        text_lines.append(f"🌅 Sunrise: {data.get('sunrise', 'N/A')}")
        text_lines.append(f"🌇 Sunset: {data.get('sunset', 'N/A')}")
        text_lines.append("")
        
        # Tithi
        if 'tithi' in data:
            text_lines.append(f"📖 Tithi: {data['tithi']['name']}")
            text_lines.append(f"   {data['tithi']['paksha']}")
            text_lines.append("")
        
        # Nakshatra
        if 'nakshatra' in data:
            text_lines.append(f"⭐ Nakshatra: {data['nakshatra']['name']}")
            if data['nakshatra']['lord']:
                text_lines.append(f"   Lord: {data['nakshatra']['lord']}")
            text_lines.append("")
        
        # Auspicious Periods
        if 'auspicious_periods' in data and data['auspicious_periods']:
            text_lines.append("✅ Auspicious Periods:")
            for period in data['auspicious_periods']:
                text_lines.append(f"   {period['name']}")
                for time_period in period['periods']:
                    text_lines.append(f"   {time_period['start']} - {time_period['end']}")
            text_lines.append("")
        
        # Inauspicious Periods
        if 'inauspicious_periods' in data and data['inauspicious_periods']:
            text_lines.append("❌ Avoid These Times:")
            for period in data['inauspicious_periods']:
                text_lines.append(f"   {period['name']}")
                for time_period in period['periods']:
                    text_lines.append(f"   {time_period['start']} - {time_period['end']}")
        
        return text_lines

    def save_formatted_data(self, data, filename=None):
        """Save formatted data to JSON file"""
        # Get the absolute path to the directory containing this script
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(BASE_DIR, "..", "..", "data")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reel_content_{timestamp}.json"
        
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            print(f"Formatted data saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    def save_reel_text(self, text_lines, filename=None):
        """Save the reel text overlay lines to a plain text file"""
        # Get the absolute path to the directory containing this script
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(BASE_DIR, "..", "..", "data")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reel_text_{timestamp}.txt"
        
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for line in text_lines:
                    f.write(line + '\n')
            print(f"Reel text overlay saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving reel text file: {e}")
            return False

# Example usage
if __name__ == "__main__":
    generator = ReelContentGenerator()
    
    print("=== Reel Content Generator ===")
    print("Fetching and formatting astrology data...")
    
    # Get formatted data
    formatted_data = generator.get_formatted_content()
    
    # Generate reel text
    reel_text = generator.generate_reel_text(formatted_data)
    
    print("\n=== Formatted Data ===")
    print(json.dumps(formatted_data, indent=2, default=str))
    
    print("\n=== Reel Text Overlay ===")
    for line in reel_text:
        print(line)
    
    # Save to file
    generator.save_formatted_data(formatted_data)
    generator.save_reel_text(reel_text)
    
    print("\n=== Ready for Image Overlay ===")
    print("Use the formatted data above to overlay text on your background image.")
    print("The 'reel_text' array contains pre-formatted lines ready for overlay.") 