#!/usr/bin/env python3
"""
TikTok Video Factory - Main Entry Point
Run the complete pipeline from idea to viral video
"""
import sys
from dotenv import load_dotenv
from orchestrator import TikTokFactoryOrchestrator, Config

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get video topic from command line or use default
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "Why most startup founders waste their first $1,000 on ads"
    
    print(f"\n🎬 TikTok Video Factory Starting...")
    print(f"📝 Topic: {topic}\n")
    
    # Create orchestrator configuration using Config dataclass
    config = Config(
        agent_01_model="gpt-4"
    )
    
    # Initialize orchestrator
    orchestrator = TikTokFactoryOrchestrator(config=config)
    
    # Run complete pipeline
    result = orchestrator.run_pipeline(topic=topic)
    
    # Display results
    print("\n" + "="*60)
    if result.get("status") == "success":
        print("✅ SUCCESS! Video generated successfully!")
        print(f"\n📁 Final Video: {result.get('final_video_path')}")
        print(f"\n📊 Pipeline Summary:")
        print(f"   - Script generated: ✓")
        print(f"   - Voice synthesized: ✓")
        print(f"   - Video created: ✓")
        print(f"   - Final composition: ✓")
    else:
        print("❌ ERROR: Pipeline failed")
        print(f"\nError message: {result.get('message', 'Unknown error')}")
    print("="*60 + "\n")
    
    return 0 if result.get("status") == "success" else 1

if __name__ == "__main__":
    sys.exit(main())
