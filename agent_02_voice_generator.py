"""
Agent 02: Voice Generator
Converts script text to speech using ElevenLabs API
"""
import os
import requests
from typing import Dict, Any
from pathlib import Path


class VoiceGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def generate_voice(self, text: str, voice_id: str = "Rachel", output_path: str = None) -> Dict[str, Any]:
        """
        Generate voice from text using ElevenLabs API
        
        Args:
            text: Script text to convert to speech
            voice_id: Voice ID to use (default: Rachel)
            output_path: Path to save audio file
            
        Returns:
            Dict with status, audio_path, and metadata
        """
        try:
            # Default output path
            if not output_path:
                output_dir = Path("output/audio")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "voiceover.mp3"
            
            # ElevenLabs API endpoint
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            
            # Make API request
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return {
                "status": "success",
                "audio_path": str(output_path),
                "voice_id": voice_id,
                "text_length": len(text),
                "message": f"Voice generated successfully: {output_path}"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Failed to generate voice: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Unexpected error: {str(e)}"
            }
    
    def list_voices(self) -> Dict[str, Any]:
        """
        List available voices from ElevenLabs
        
        Returns:
            Dict with available voices
        """
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return {
                "status": "success",
                "voices": response.json()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


def run(script_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for Agent 02
    
    Args:
        script_result: Output from Agent 01 containing the script
        
    Returns:
        Dict with voice generation results
    """
    if script_result.get("status") != "success":
        return {
            "status": "error",
            "message": "Cannot generate voice: script generation failed",
            "upstream_error": script_result
        }
    
    script_text = script_result.get("script", "")
    
    if not script_text:
        return {
            "status": "error",
            "message": "No script text found in input"
        }
    
    generator = VoiceGenerator()
    result = generator.generate_voice(script_text)
    
    # Add script info to result
    result["script_used"] = script_text[:100] + "..." if len(script_text) > 100 else script_text
    
    return result


if __name__ == "__main__":
    # Test with sample script
    test_input = {
        "status": "success",
        "script": "This is a test voiceover for TikTok video generation."
    }
    
    result = run(test_input)
    print(result)
