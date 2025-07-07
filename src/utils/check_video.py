import cv2
import os

def check_video_properties(video_path):
    """Check video properties to verify all segments"""
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video file")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps
    
    print(f"Video Properties:")
    print(f"  Path: {video_path}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  FPS: {fps}")
    print(f"  Frame count: {frame_count}")
    print(f"  Dimensions: {width}x{height}")
    
    # Calculate expected frame count for 26 seconds
    expected_frames = 26 * fps
    print(f"  Expected frames for 26s: {expected_frames}")
    print(f"  Actual frames: {frame_count}")
    
    if abs(frame_count - expected_frames) < 10:  # Allow small difference
        print("✅ Video duration matches expected 26 seconds")
    else:
        print("❌ Video duration does not match expected 26 seconds")
    
    cap.release()

if __name__ == "__main__":
    # Find the latest video file
    output_dir = "output_videos"
    if os.path.exists(output_dir):
        video_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
        if video_files:
            latest_video = sorted(video_files)[-1]  # Get the latest file
            video_path = os.path.join(output_dir, latest_video)
            print(f"Checking latest video: {latest_video}")
            check_video_properties(video_path)
        else:
            print("No video files found in output_videos directory")
    else:
        print("output_videos directory not found") 