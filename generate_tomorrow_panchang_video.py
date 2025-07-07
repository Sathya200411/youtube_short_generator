#!/usr/bin/env python3
"""
Master script to generate tomorrow's panchang video
Runs all generators in sequence:
1. Reel content generator (gets tomorrow's data)
2. Image overlay generator (creates images)
3. Video generator (creates final video)
"""

import sys
import os

# Add the src/generators directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'generators'))

from reel_content_generator import ReelContentGenerator
from image_overlay_generator import ImageOverlayGenerator
from video_generator import VideoGenerator

def main():
    print("=== Tomorrow's Panchang Video Generator ===")
    print("This will generate a complete video for tomorrow's panchang.")
    print()
    
    try:
        # Step 1: Generate tomorrow's content
        print("Step 1: Fetching tomorrow's panchang data...")
        content_generator = ReelContentGenerator()
        formatted_data = content_generator.get_formatted_content()
        
        if not formatted_data:
            print("❌ Failed to get panchang data")
            return False
        
        print("✅ Tomorrow's panchang data fetched successfully")
        print(f"Date: {formatted_data.get('date', 'N/A')}")
        print()
        
        # Step 2: Generate reel text
        print("Step 2: Generating reel text overlay...")
        reel_text = content_generator.generate_reel_text(formatted_data)
        
        if not reel_text:
            print("❌ Failed to generate reel text")
            return False
        
        print("✅ Reel text generated successfully")
        print(f"Text lines: {len(reel_text)}")
        print()
        
        # Step 3: Create image overlays
        print("Step 3: Creating image overlays...")
        image_generator = ImageOverlayGenerator()
        
        # Preview content division
        image_generator.preview_content_division(reel_text)
        
        # Generate images
        success = image_generator.generate_images(reel_text)
        
        if not success:
            print("❌ Failed to generate images")
            return False
        
        print("✅ Images generated successfully")
        print()
        
        # Step 4: Generate video
        print("Step 4: Generating final video...")
        video_generator = VideoGenerator()
        success = video_generator.generate_video()
        
        if not success:
            print("❌ Failed to generate video")
            return False
        
        print("✅ Video generated successfully!")
        print()
        
        # Final summary
        print("=== Generation Complete ===")
        print("✅ Tomorrow's panchang video has been created successfully!")
        print("📁 Check the 'output_videos' folder for your video file.")
        print("📅 Video contains data for:", formatted_data.get('date', 'N/A'))
        print("🎬 Video duration: 26 seconds")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("🎉 All done! Your tomorrow's panchang video is ready.")
    else:
        print("💥 Generation failed. Please check the error messages above.") 