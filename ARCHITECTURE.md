# TikTok Viral Video Factory - Architecture

## Overview
End-to-end automated pipeline: **Idea → Script → Voice → Visuals → Video → Post → Analytics → Feedback Loop**

## Pipeline Agents

### ✅ Agent 01: Script Generator
**Status:** COMPLETED
**Input:** Topic/idea (string)
**Output:** Structured JSON script with timestamps, hooks, CTAs
**Tech:** OpenAI GPT-4 API with Structured Outputs
**Features:** Viral patterns, retry logic, cost tracking

### 🔄 Agent 02: Voice Generator  
**Input:** Script JSON from Agent 01
**Output:** MP3/WAV audio file
**Tech:** ElevenLabs TTS API
**Features:** Multiple voice personas, timing alignment, audio quality optimization

### 🔄 Agent 03: Visual Generator
**Input:** Script JSON + timing data
**Output:** Video clips/scenes
**Tech:** Pexels/Unsplash APIs (stock footage) OR Runway ML (AI generation)
**Features:** Scene matching, stock footage search, AI video generation

### 🔄 Agent 04: Video Compositor
**Input:** Audio file + visual clips + script JSON
**Output:** Final TikTok video (MP4)
**Tech:** FFmpeg
**Features:** Audio/video sync, text overlays, transitions, captions

### 🔄 Agent 05: TikTok Uploader
**Input:** Final video file + caption + hashtags
**Output:** Published TikTok post
**Tech:** TikTok Content Posting API
**Features:** Auto-post, scheduling, caption optimization

### 🔄 Agent 06: Analytics Collector
**Input:** Posted video IDs
**Output:** Performance metrics JSON
**Tech:** TikTok Research API / Analytics API
**Features:** Views, likes, shares, watch time, completion rate

### 🔄 Agent 07: Feedback Analyzer
**Input:** Analytics data + original script
**Output:** Insights and improvement recommendations
**Tech:** OpenAI GPT-4 analysis
**Features:** Performance analysis, pattern detection, script optimization suggestions

## Orchestrator

**Main Pipeline Controller:**
```python
def run_video_factory(topic: str, persona: str = "energetic"):
    # 1. Generate script
    script = agent_01.generate_script(topic)
    
    # 2. Generate voice
    audio = agent_02.generate_voice(script, persona)
    
    # 3. Generate visuals
    visuals = agent_03.generate_visuals(script)
    
    # 4. Compose video
    video = agent_04.compose_video(audio, visuals, script)
    
    # 5. Upload to TikTok
    post_id = agent_05.upload_video(video, script)
    
    # 6. Wait for analytics (24h)
    time.sleep(86400)
    
    # 7. Collect analytics
    analytics = agent_06.collect_analytics(post_id)
    
    # 8. Generate feedback
    feedback = agent_07.analyze_performance(script, analytics)
    
    # 9. Store for future learning
    store_feedback(feedback)
    
    return {"post_id": post_id, "analytics": analytics, "feedback": feedback}
```

## Feedback Loop

**How videos get better over time:**

1. **Data Collection:** Every posted video stores:
   - Original script parameters
   - Performance metrics
   - Engagement patterns

2. **Pattern Recognition:**
   - High-performing hooks
   - Effective CTAs  
   - Optimal video length
   - Best performing topics

3. **Script Improvement:**
   - Agent 01 accesses historical data
   - Incorporates successful patterns
   - Avoids unsuccessful approaches
   - A/B tests new variations

## API Requirements & Costs

### Required APIs:
1. **OpenAI API** - Script generation & feedback analysis
   - Cost: ~$0.002-0.01 per script
   
2. **ElevenLabs API** - Voice generation
   - Cost: ~$0.30 per 1000 characters
   
3. **Pexels/Unsplash API** - Stock footage (FREE tier available)
   - OR Runway ML - AI video ($0.05/sec generated)
   
4. **TikTok Content Posting API** - Upload videos
   - Requires TikTok Developer Account (FREE)
   
5. **TikTok Research/Analytics API** - Performance metrics
   - Requires approval (FREE for research)

### Total Cost Per Video:
- Script: $0.01
- Voice: $0.50  
- Visuals: $0 (stock) or $3 (AI)
- Upload: $0
- Analytics: $0
**Total: $0.51 - $3.51 per video**

## File Structure

```
viral-ai-video-factory/
├── agent_01_script_generator.py ✅
├── agent_02_voice_generator.py
├── agent_03_visual_generator.py
├── agent_04_video_compositor.py
├── agent_05_tiktok_uploader.py
├── agent_06_analytics_collector.py
├── agent_07_feedback_analyzer.py
├── orchestrator.py
├── config.py
├── requirements.txt
├── .env.example
├── outputs/
│   ├── scripts/
│   ├── audio/
│   ├── visuals/
│   ├── videos/
│   └── analytics/
└── data/
    ├── feedback.json
    └── performance_history.json
```

## Next Steps

1. ✅ Complete Agent 01 (DONE)
2. 🔄 Build Agent 02 (Voice Generator)
3. 🔄 Build Agent 03 (Visual Generator) 
4. 🔄 Build Agent 04 (Video Compositor)
5. 🔄 Set up TikTok Developer Account
6. 🔄 Build Agent 05 (TikTok Uploader)
7. 🔄 Build Agent 06 (Analytics Collector)
8. 🔄 Build Agent 07 (Feedback Analyzer)
9. 🔄 Build Orchestrator
10. 🔄 Test end-to-end pipeline
11. 🔄 Deploy & monitor first batch of videos
12. 🔄 Analyze feedback loop performance

## Timeline
- **Phase 1 (Today):** Agents 01-04 (Script → Video file)
- **Phase 2 (Tomorrow):** Agents 05-06 (Upload → Analytics)
- **Phase 3 (Day 3):** Agent 07 + Orchestrator (Feedback loop)
- **Phase 4 (Day 4+):** Testing & optimization

## Success Metrics
- Videos posted per day
- Average view count
- Engagement rate
- Script quality improvement over time
- Cost per 1000 views
