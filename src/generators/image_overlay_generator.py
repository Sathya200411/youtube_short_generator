from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime
import os
import re

class ImageOverlayGenerator:
    def __init__(self, background_path=None):
        # Get the absolute path to the directory containing this script
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        if background_path is None:
            self.background_path = os.path.join(BASE_DIR, "..", "..", "assets", "images", "background.jpg")
        else:
            self.background_path = background_path
        self.output_dir = os.path.join(BASE_DIR, "..", "..", "output_images")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
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
        
        # Calculate text positioning
        img_width, img_height = image.size
        line_height = font_size + 10
        total_text_height = len(text_lines) * line_height
        
        # Start position (center vertically)
        start_y = (img_height - total_text_height) // 2
        
        # Draw each line of text centered horizontally
        for i, line in enumerate(text_lines):
            y_position = start_y + (i * line_height)
            # Calculate width of the text to center it
            try:
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
            except AttributeError:
                text_width, _ = draw.textsize(line, font=font)
            x_position = (img_width - text_width) // 2
            draw.text((x_position, y_position), line, fill=text_color, font=font)
        
        return image
    
    def divide_content(self, reel_text):
        """Divide the content into 2 parts, keeping headings and their associated lines together"""
        # Group lines: a group is a heading and its following lines (until next heading or end)
        groups = []
        current_group = []
        heading_keywords = [
            'Tithi:', 'Nakshatra:', 'Auspicious Periods:', 'Avoid These Times:',
            'Sunrise:', 'Sunset:', 'Lord:', 'Paksha', 'Muhurat', 'Kaal', 'Dur Muhurat', 'Varjyam', 'Rahu', 'Yamaganda', 'Gulika'
        ]
        def is_heading(line):
            # Consider a heading if it ends with ':' or matches a known keyword
            return any(kw in line for kw in heading_keywords) or (line.strip().endswith(':'))
        for line in reel_text:
            if is_heading(line) and current_group:
                groups.append(current_group)
                current_group = [line]
            else:
                current_group.append(line)
        if current_group:
            groups.append(current_group)
        # Now split groups as evenly as possible
        total_lines = sum(len(g) for g in groups)
        half_lines = total_lines // 2
        part1, part2 = [], []
        count = 0
        for group in groups:
            if count < half_lines:
                part1.extend(group)
                count += len(group)
            else:
                part2.extend(group)
        return part1, part2
    
    def remove_emojis(self, text):
        emoji_pattern = re.compile("[\U00010000-\U0010ffff]|[\u2600-\u26FF\u2700-\u27BF]", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)
    
    def generate_images(self, reel_text):
        """Generate two images with divided content, removing emojis and cleaning output folder"""
        # Clean output directory
        for f in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
        # Load background
        background = self.load_background()
        if not background:
            print("Failed to load background image")
            return False
        # Divide content
        part1, part2 = self.divide_content(reel_text)
        # Remove emojis from each line
        part1 = [self.remove_emojis(line) for line in part1]
        part2 = [self.remove_emojis(line) for line in part2]
        # Generate first image
        img1 = background.copy()
        img1 = self.create_text_overlay(img1, part1)
        # Generate second image
        img2 = background.copy()
        img2 = self.create_text_overlay(img2, part2)
        # Save images (always use same filenames)
        img1_path = os.path.join(self.output_dir, "reel_part1.jpg")
        img2_path = os.path.join(self.output_dir, "reel_part2.jpg")
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
    # Sample reel text (you can replace this with actual content from your generator)
    sample_reel_text = [
        "📅 06 July 2025",
        "🌅 Sunrise: 06:10 AM",
        "🌇 Sunset: 07:17 PM",
        "",
        "📖 Tithi: Ekadashi",
        "   Shukla Paksha",
        "",
        "⭐ Nakshatra: Vishaka",
        "   Lord: Jupiter",
        "",
        "✅ Auspicious Periods:",
        "   Abhijit Muhurat",
        "   12:17 PM - 01:09 PM",
        "   Amrit Kaal",
        "   12:50 PM - 02:37 PM",
        "   Brahma Muhurat",
        "   04:34 AM - 05:22 AM",
        "",
        "❌ Avoid These Times:",
        "   Rahu",
        "   05:38 PM - 07:16 PM",
        "   Yamaganda",
        "   12:43 PM - 02:22 PM",
        "   Gulika",
        "   04:00 PM - 05:38 PM",
        "   Dur Muhurat",
        "   05:32 PM - 06:24 PM",
        "   Varjyam",
        "   03:06 AM - 04:52 AM"
    ]
    
    generator = ImageOverlayGenerator()
    
    # Preview content division
    generator.preview_content_division(sample_reel_text)
    
    # Generate images
    success = generator.generate_images(sample_reel_text)
    
    if success:
        print("\n✅ Images generated successfully!")
        print("Check the 'output_images' folder for your reel images.")
    else:
        print("\n❌ Failed to generate images.") 