import os
from datetime import date
from PIL import Image, ImageDraw, ImageFont

def create_thumbnail(output_path="podcast_thumbnail.png"):
    """
    Dynamically generates a YouTube-optimized thumbnail using Pillow.
    Uses a dark gradient background, embeds the official PulseAI logo, and writes text.
    """
    import textwrap
    width, height = 1920, 1080
    # Create dark background
    image = Image.new("RGB", (width, height), "#0f1117")
    draw = ImageDraw.Draw(image)
    
    # Try to load a nice font, fallback to default
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 90)
        subtitle_font = ImageFont.truetype("arial.ttf", 50)
    except IOError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Paste the User's PulseAI Logo
    try:
        logo_path = r"c:\Users\srisa\Downloads\PulseAI\pulseai_linkedin_logo_1776327928614.png"
        logo = Image.open(logo_path).convert("RGBA")
        
        # Resize logo to 500x500
        logo = logo.resize((500, 500), Image.Resampling.LANCZOS)
        
        # Paste horizontally centered, starting a bit from the top
        logo_x = (width - 500) // 2
        logo_y = 150
        image.paste(logo, (logo_x, logo_y), logo)
    except Exception as e:
        print(f"Warning: Could not load logo: {e}")

    # Draw Brand Text
    brand_text = "PulseAI Daily Podcast"
    draw.text(((width - draw.textlength(brand_text, font=title_font)) // 2, 720), brand_text, fill="#f1f5f9", font=title_font)
    
    # Draw Date beneath it
    today_str = date.today().strftime("%B %d, %Y")
    date_text = f"The biggest AI updates for {today_str}"
    draw.text(((width - draw.textlength(date_text, font=subtitle_font)) // 2, 850), date_text, fill="#3b82f6", font=subtitle_font)
    
    # Draw Footer
    footer_text = "Listen to the full automated podcast now."
    draw.text(((width - draw.textlength(footer_text, font=subtitle_font)) // 2, 980), footer_text, fill="#64748b", font=subtitle_font)
    
    image.save(output_path)
    return output_path

def generate_mp4_from_audio(audio_path: str, thumbnail_path: str = None, output_path: str = "pulseai_video.mp4") -> str:
    """
    Takes an MP3 file and a static image thumbnail, and compiles them into
    an MP4 video file optimized for YouTube using MoviePy 2.x.
    """
    try:
        from moviepy import AudioFileClip, ImageClip
        
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            thumbnail_path = create_thumbnail()
            
        print("Rendering Video with MoviePy...")
        # Load audio
        audio = AudioFileClip(audio_path)
        
        # Load image and set its duration to match the audio perfectly
        image = ImageClip(thumbnail_path).with_duration(audio.duration)
        
        # Set the audio of the image clip
        video = image.with_audio(audio)
        
        # Write the video file (fps=1 is perfectly fine for a static image, reduces render time)
        video.write_videofile(output_path, fps=1, codec="libx264", audio_codec="aac")
        
        print(f"Video saved to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Failed to render Video: {e}")
        return ""
