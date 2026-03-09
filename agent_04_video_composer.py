"""
Agent 04: Video Composer
Combines audio and video using FFmpeg
"""
import os
import subprocess
from typing import Dict, Any
from pathlib import Path


class VideoComposer:
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"  # Assumes ffmpeg is in PATH
        
    def compose_video(self, video_path: str, audio_path: str, output_path: str = None) -> Dict[str, Any]:
        """
        Combine video and audio tracks using FFmpeg
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path for final composed video
            
        Returns:
            Dict with status, final_video_path, and metadata
        """
        try:
            # Validate input files
            if not os.path.exists(video_path):
                return {
                    "status": "error",
                    "message": f"Video file not found: {video_path}"
                }
            
            if not os.path.exists(audio_path):
                return {
                    "status": "error",
                    "message": f"Audio file not found: {audio_path}"
                }
            
            # Default output path
            if not output_path:
                output_dir = Path("output/final")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "final_video.mp4"
            
            # FFmpeg command to combine video and audio
            ffmpeg_command = [
                self.ffmpeg_path,
                "-i", str(video_path),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-y",
                str(output_path)
            ]
            
            # Run FFmpeg
            result = subprocess.run(
                ffmpeg_command,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Verify output file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                
                return {
                    "status": "success",
                    "final_video_path": str(output_path),
                    "input_video": str(video_path),
                    "input_audio": str(audio_path),
                    "file_size_bytes": file_size,
                    "message": f"Video composed successfully: {output_path}"
                }
            else:
                return {
                    "status": "error",
                    "message": "Output file was not created"
                }
                
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error": str(e),
                "stderr": e.stderr,
                "message": f"FFmpeg error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Unexpected error: {str(e)}"
            }


def run(video_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for Agent 04
    
    Args:
        video_result: Output from Agent 03 containing video and audio paths
        
    Returns:
        Dict with final composed video results
    """
    if video_result.get("status") != "success":
        return {
            "status": "error",
            "message": "Cannot compose video: video generation failed",
            "upstream_error": video_result
        }
    
    video_path = video_result.get("video_path")
    audio_path = video_result.get("audio_path")
    
    if not video_path or not audio_path:
        return {
            "status": "error",
            "message": "Missing video_path or audio_path in input"
        }
    
    composer = VideoComposer()
    result = composer.compose_video(video_path, audio_path)
    
    # Add metadata from previous steps
    result["pipeline_metadata"] = {
        "script_prompt": video_result.get("visual_prompt_used", ""),
        "video_source": video_path,
        "audio_source": audio_path
    }
    
    return result


if __name__ == "__main__":
    # Test with sample paths
    test_input = {
        "status": "success",
        "video_path": "output/videos/generated_video.mp4",
        "audio_path": "output/audio/voiceover.mp3",
        "visual_prompt_used": "Test visual prompt"
    }
    
    result = run(test_input)
    print(result)
