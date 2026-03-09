"""
Agent 03: Video Generator
Generates visual content using Runway ML API
"""
import os
import requests
import time
from typing import Dict, Any
from pathlib import Path


class VideoGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('RUNWAYML_API_KEY')
        self.base_url = "https://api.runwayml.com/v1"
        
    def generate_video(self, prompt: str, duration: int = 5, output_path: str = None) -> Dict[str, Any]:
        """
        Generate video from text prompt using Runway ML API
        
        Args:
            prompt: Visual description for video generation
            duration: Video duration in seconds (default: 5)
            output_path: Path to save video file
            
        Returns:
            Dict with status, video_path, and metadata
        """
        try:
            # Default output path
            if not output_path:
                output_dir = Path("output/videos")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "generated_video.mp4"
            
            # Runway ML Gen-2 API endpoint
            url = f"{self.base_url}/gen2/generate"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "duration": duration,
                "resolution": "1080p",
                "aspect_ratio": "9:16",  # TikTok format
                "model": "gen2"
            }
            
            # Start video generation
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            if not task_id:
                return {
                    "status": "error",
                    "message": "Failed to start video generation"
                }
            
            # Poll for completion
            max_attempts = 60  # 5 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                status_url = f"{self.base_url}/tasks/{task_id}"
                status_response = requests.get(status_url, headers=headers)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                status = status_data.get("status")
                
                if status == "SUCCEEDED":
                    video_url = status_data.get("output", {}).get("url")
                    
                    if video_url:
                        # Download video
                        video_response = requests.get(video_url)
                        video_response.raise_for_status()
                        
                        with open(output_path, 'wb') as f:
                            f.write(video_response.content)
                        
                        return {
                            "status": "success",
                            "video_path": str(output_path),
                            "task_id": task_id,
                            "prompt": prompt,
                            "duration": duration,
                            "message": f"Video generated successfully: {output_path}"
                        }
                    else:
                        return {
                            "status": "error",
                            "message": "Video URL not found in response"
                        }
                        
                elif status == "FAILED":
                    return {
                        "status": "error",
                        "message": f"Video generation failed: {status_data.get('error', 'Unknown error')}"
                    }
                
                # Wait before next poll
                time.sleep(5)
                attempt += 1
            
            return {
                "status": "error",
                "message": "Video generation timed out"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Unexpected error: {str(e)}"
            }


def run(voice_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for Agent 03
    
    Args:
        voice_result: Output from Agent 02 containing audio file path
        
    Returns:
        Dict with video generation results
    """
    if voice_result.get("status") != "success":
        return {
            "status": "error",
            "message": "Cannot generate video: voice generation failed",
            "upstream_error": voice_result
        }
    
    # Extract script or use default prompt
    script = voice_result.get("script_used", "")
    
    # Create visual prompt from script
    # In a real implementation, this could use GPT-4 to convert script to visual prompts
    visual_prompt = f"Cinematic TikTok video: {script[:200]}"
    
    generator = VideoGenerator()
    result = generator.generate_video(visual_prompt)
    
    # Add upstream info to result
    result["audio_path"] = voice_result.get("audio_path", "")
    result["visual_prompt_used"] = visual_prompt
    
    return result


if __name__ == "__main__":
    # Test with sample input
    test_input = {
        "status": "success",
        "audio_path": "output/audio/voiceover.mp3",
        "script_used": "This is a test video for TikTok generation."
    }
    
    result = run(test_input)
    print(result)
