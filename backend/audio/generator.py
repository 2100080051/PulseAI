import os
import asyncio
import edge_tts

# For a highly conversational, energetic female tech voice (less robotic than standard)
DEFAULT_VOICE = "en-US-AriaNeural"

async def _generate_audio_async(text: str, output_path: str, voice: str):
    """Internal async function to communicate with Microsoft Edge TTS."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_podcast_audio(script_text: str, output_path: str = "pulseai_podcast.mp3") -> str:
    """
    Takes the podcast script and converts it to a high-quality human-like MP3 file 
    using Edge TTS. Runs the async loop synchronously for ease of use in Streamlit.
    """
    if not script_text:
        return ""
        
    try:
        asyncio.run(_generate_audio_async(script_text, output_path, DEFAULT_VOICE))
        return output_path
    except Exception as e:
        print(f"TTS Engine Error: {e}")
        return ""
