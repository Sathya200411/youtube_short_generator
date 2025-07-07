from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime
import os
import requests
import pytz

class ReelImageGenerator:
    def __init__(self, background_path="background.jpg"):
        self.background_path = background_path
        self.output_dir = "output_images"
        self.client_id = "efd2aa11-ce98-49e5-a04a-dfb5277d6856"
        self.client_secret = "0GMhVTymCt6t4eTO1ugpgiTc4ghIYXsfOfroZKKD"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
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
            response = requests.get(f"https://api.prokerala.com/v2/astrology/{endpoint}", 
                                  headers=headers, params=params, timeout=30)
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
        
        # Set default datetime if not provided
        if not datetime_str:
            tz = pytz.timezone(timezone_str)
            datetime_str = datetime.now(tz).isoformat()
        
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
        """Generate formatted text for reel overlays (no emojis, no left padding)"""
        text_lines = []
        
        # Header
        text_lines.append(f"{data['date']}")
        text_lines.append(f"Sunrise: {data.get('sunrise', 'N/A')}")
        text_lines.append(f"Sunset: {data.get('sunset', 'N/A')}")
        text_lines.append("")
        
        # Tithi
        if 'tithi' in data:
            text_lines.append(f"Tithi: {data['tithi']['name']}")
            text_lines.append(f"{data['tithi']['paksha']}")
            text_lines.append("")
        
        # Nakshatra
        if 'nakshatra' in data:
            text_lines.append(f"Nakshatra: {data['nakshatra']['name']}")
            if data['nakshatra']['lord']:
                text_lines.append(f"Lord: {data['nakshatra']['lord']}")
            text_lines.append("")
        
        # Auspicious Periods
        if 'auspicious_periods' in data and data['auspicious_periods']:
            text_lines.append("Auspicious Periods:")
            for period in data['auspicious_periods']:
                text_lines.append(f"{period['name']}")
                for time_period in period['periods']:
                    text_lines.append(f"{time_period['start']} - {time_period['end']}")
            text_lines.append("")
        
        # Inauspicious Periods
        if 'inauspicious_periods' in data and data['inauspicious_periods']:
            text_lines.append("Avoid These Times:")
            for period in data['inauspicious_periods']:
                text_lines.append(f"{period['name']}")
                for time_period in period['periods']:
                    text_lines.append(f"{time_period['start']} - {time_period['end']}")
        
        return text_lines

    def load_background(self):
        """Load the background image"""
        try:
            return Image.open(self.background_path)
        except Exception as e:
            print(f"Error loading background image: {e}")
            return None
    
    def create_text_overlay(self, image, text_lines, font_size=40, text_color=(0, 0, 0)):
        """Create text overlay on the image, center-aligned and black text"""
        draw = ImageDraw.Draw(image)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        img_width, img_height = image.size
        line_height = font_size + 10
        total_text_height = len(text_lines) * line_height
        start_y = (img_height - total_text_height) // 2
        
        for i, line in enumerate(text_lines):
            y_position = start_y + (i * line_height)
            # Calculate text width for center alignment
            try:
                # Pillow >=8.0.0
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            except AttributeError:
                # Fallback for older Pillow
                text_width = font.getsize(line)[0]
            x_position = (img_width - text_width) // 2
            # Add shadow for readability (optional, can remove if not needed)
            shadow_offset = 2
            draw.text((x_position + shadow_offset, y_position + shadow_offset), 
                     line, fill=(200, 200, 200), font=font)  # Light shadow
            draw.text((x_position, y_position), line, fill=text_color, font=font)
        
        return image
    
    def divide_content(self, reel_text):
        """Divide the content into 2 parts"""
        total_lines = len(reel_text)
        mid_point = total_lines // 2
        
        part1 = reel_text[:mid_point]
        part2 = reel_text[mid_point:]
        
        return part1, part2
    
    def generate_images(self, reel_text):
        """Generate two images with divided content"""
        # Load background
        background = self.load_background()
        if not background:
            print("Failed to load background image")
            return False
        
        # Divide content
        part1, part2 = self.divide_content(reel_text)
        
        # Generate first image
        img1 = background.copy()
        img1 = self.create_text_overlay(img1, part1)
        
        # Generate second image
        img2 = background.copy()
        img2 = self.create_text_overlay(img2, part2)
        
        # Save images
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img1_path = os.path.join(self.output_dir, f"reel_part1_{timestamp}.jpg")
        img2_path = os.path.join(self.output_dir, f"reel_part2_{timestamp}.jpg")
        
        img1.save(img1_path, "JPEG", quality=95)
        img2.save(img2_path, "JPEG", quality=95)
        
        print(f"Generated images:")
        print(f"Part 1: {img1_path}")
        print(f"Part 2: {img2_path}")
        
        return True
    
    def preview_content_division(self, reel_text):
        """Preview how content will be divided"""
        part1, part2 = self.divide_content(reel_text)
        
        print("=== Content Division Preview ===")
        print("\n--- PART 1 ---")
        for line in part1:
            print(line)
        
        print("\n--- PART 2 ---")
        for line in part2:
            print(line)
        print("=" * 50)

# Example usage
if __name__ == "__main__":
    generator = ReelImageGenerator()
    
    print("=== Reel Image Generator ===")
    print("Fetching astrology data and generating images...")
    
    # Get formatted data
    formatted_data = generator.get_formatted_content()
    
    # Generate reel text
    reel_text = generator.generate_reel_text(formatted_data)
    
    print("\n=== Generated Content ===")
    for line in reel_text:
        print(line)
    
    # Preview content division
    generator.preview_content_division(reel_text)
    
    # Generate images
    success = generator.generate_images(reel_text)
    
    if success:
        print("\n✅ Images generated successfully!")
        print("Check the 'output_images' folder for your reel images.")
    else:
        print("\n❌ Failed to generate images.") 