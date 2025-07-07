import sys
import os
from datetime import datetime

# Get the absolute path to the directory containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add Windows Python 3.13 site-packages path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import re

class VideoGenerator:
    def __init__(self):
        self.first_image_path = os.path.join(BASE_DIR, "..", "..", "assets", "images", "first image.png")
        self.last_image_path = os.path.join(BASE_DIR, "..", "..", "assets", "images", "last image.jpg")
        self.reel_part1_path = os.path.join(BASE_DIR, "..", "..", "output_images", "reel_part1.jpg")
        self.reel_part2_path = os.path.join(BASE_DIR, "..", "..", "output_images", "reel_part2.jpg")
        self.output_dir = os.path.join(BASE_DIR, "..", "..", "output_videos")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def add_date_to_image(self, image_path, date_text):
        """Add date text and 'panchang' to the top center of an image"""
        try:
            # Open image with PIL
            pil_image = Image.open(image_path)
            
            # Get image dimensions first
            img_width, img_height = pil_image.size
            
            # Calculate font sizes
            date_font_size = int(img_width / 15)  # 1/15th of image width
            panchang_font_size = int(img_width / 20)  # slightly smaller
            
            # Create a drawing object
            draw = ImageDraw.Draw(pil_image)
            
            # Try to use a default font, fallback to basic if not available
            try:
                date_font = ImageFont.truetype("arial.ttf", date_font_size)
            except:
                try:
                    date_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", date_font_size)
                except:
                    date_font = ImageFont.load_default()
            try:
                panchang_font = ImageFont.truetype("arial.ttf", panchang_font_size)
            except:
                try:
                    panchang_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", panchang_font_size)
                except:
                    panchang_font = ImageFont.load_default()
            
            # Calculate text position for date (top center)
            try:
                bbox = date_font.getbbox(date_text)
                date_text_width = bbox[2] - bbox[0]
                date_text_height = bbox[3] - bbox[1]
            except AttributeError:
                date_text_width, date_text_height = draw.textsize(date_text, font=date_font)
            x_position = (img_width - date_text_width) // 2
            y_position = 50  # 50 pixels from top
            # Draw date text
            draw.text((x_position, y_position), date_text, fill=(0, 0, 0), font=date_font)
            
            # Calculate text position for 'panchang' (centered below date)
            panchang_text = "panchang"
            try:
                bbox = panchang_font.getbbox(panchang_text)
                panchang_text_width = bbox[2] - bbox[0]
                panchang_text_height = bbox[3] - bbox[1]
            except AttributeError:
                panchang_text_width, panchang_text_height = draw.textsize(panchang_text, font=panchang_font)
            panchang_x = (img_width - panchang_text_width) // 2
            panchang_y = y_position + date_text_height + 10  # 10 pixels below date
            # Draw 'panchang' text
            draw.text((panchang_x, panchang_y), panchang_text, fill=(0, 0, 0), font=panchang_font)
            
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return cv_image
        except Exception as e:
            print(f"Error adding date to image: {e}")
            return None
    
    def load_image(self, image_path):
        """Load image and convert to OpenCV format"""
        try:
            return cv2.imread(image_path)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def resize_image(self, image, target_width=1080, target_height=1920):
        """Resize image to target dimensions (portrait format for reels)"""
        if image is None:
            return None
        return cv2.resize(image, (target_width, target_height))
    
    def create_video_segment(self, image, duration_seconds, fps=30):
        """Create video frames for a given image and duration"""
        if image is None:
            return []
        
        total_frames = int(duration_seconds * fps)
        frames = []
        
        for _ in range(total_frames):
            frames.append(image.copy())
        
        return frames
    
    def generate_video(self, fps=30):
        """Generate the complete video with all segments"""
        print("Starting video generation...")
        
        # Get tomorrow's date for first image
        from datetime import timedelta
        tomorrow = datetime.now() + timedelta(days=1)
        current_date = tomorrow.strftime("%d %B %Y")
        print(f"Adding date '{current_date}' to first image...")
        
        # Load and process first image (with date)
        first_image = self.add_date_to_image(self.first_image_path, current_date)
        if first_image is None:
            print("Failed to load first image")
            return False
        
        # Load other images
        reel_part1 = self.load_image(self.reel_part1_path)
        reel_part2 = self.load_image(self.reel_part2_path)
        last_image = self.load_image(self.last_image_path)
        
        if reel_part1 is None or reel_part2 is None or last_image is None:
            print("Failed to load one or more images")
            return False
        
        # Resize all images to same dimensions (portrait format for reels)
        target_width, target_height = 1080, 1920
        first_image = self.resize_image(first_image, target_width, target_height)
        reel_part1 = self.resize_image(reel_part1, target_width, target_height)
        reel_part2 = self.resize_image(reel_part2, target_width, target_height)
        last_image = self.resize_image(last_image, target_width, target_height)
        
        print("Creating video segments...")
        
        # Create video segments
        segment1_frames = self.create_video_segment(first_image, 3, fps)  # 3 seconds
        segment2_frames = self.create_video_segment(reel_part1, 10, fps)  # 10 seconds
        segment3_frames = self.create_video_segment(reel_part2, 10, fps)  # 10 seconds
        segment4_frames = self.create_video_segment(last_image, 3, fps)   # 3 seconds
        
        # Combine all frames
        all_frames = segment1_frames + segment2_frames + segment3_frames + segment4_frames
        
        print(f"Total frames: {len(all_frames)}")
        print(f"Expected duration: {len(all_frames)/fps:.1f} seconds")
        
        # Clean output directory - delete any existing videos
        for f in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, f)
            if os.path.isfile(file_path) and f.endswith('.mp4'):
                os.remove(file_path)
                print(f"Deleted existing video: {f}")
        
        # Create video writer with fixed filename
        output_path = os.path.join(self.output_dir, "reel_video.mp4")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
        
        if not out.isOpened():
            print("Failed to create video writer")
            return False
        
        print("Writing frames to video...")
        
        # Write frames to video
        for i, frame in enumerate(all_frames):
            out.write(frame)
            if i % fps == 0:  # Print progress every second
                print(f"Progress: {i//fps}/{len(all_frames)//fps} seconds")
        
        # Release video writer
        out.release()
        
        print(f"Video generated successfully: {output_path}")
        print(f"Video duration: {len(all_frames)/fps:.1f} seconds")
        
        return True

# Example usage
if __name__ == "__main__":
    generator = VideoGenerator()
    
    print("=== Video Generator ===")
    print("Creating reel video with 4 segments:")
    print("1. First image with date (3 seconds)")
    print("2. Reel part 1 (10 seconds)")
    print("3. Reel part 2 (10 seconds)")
    print("4. Last image (3 seconds)")
    print("Total duration: 26 seconds")
    print()
    
    success = generator.generate_video()
    
    if success:
        print("\n✅ Video generated successfully!")
        print("Check the 'output_videos' folder for your reel video.")
    else:
        print("\n❌ Failed to generate video.") 