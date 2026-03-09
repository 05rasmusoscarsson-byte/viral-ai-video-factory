# Setup Guide for TikTok Video Factory

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- API keys for:
  - OpenAI (GPT-4)
  - ElevenLabs (Voice generation)
  - Runway ML (Video generation)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/05rasmusoscarsson-byte/viral-ai-video-factory.git
cd viral-ai-video-factory
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Mac (using Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. Configure API Keys

Create a `.env` file in the project root directory:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys:

```
OPENAI_API_KEY=sk-proj-...
ELEVENLABS_API_KEY=sk_...
RUNWAYML_API_SECRET=...
```

#### How to Get API Keys:

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Name it "TikTok Video Factory"
4. Copy the key and paste it in your `.env` file

**ElevenLabs API Key:**
1. Go to https://elevenlabs.io/app/developers/api-keys
2. Click "Create API Key"
3. Name it "TikTok Video Factory"
4. Copy the key and paste it in your `.env` file

**Runway ML API Key:**
1. Go to https://dev.runwayml.com/
2. Sign in and create an organization
3. Navigate to API Keys section
4. Click "+ New API Key"
5. Name it "TikTok Video Factory"
6. Copy the key and paste it in your `.env` file

### 5. Configure Content Profiles (Optional)

The `content_profiles.json` file contains multiple TikTok account profiles for different content niches. You can customize these profiles or add your own.

See `MULTI_ACCOUNT_GUIDE.md` for detailed instructions on managing multiple TikTok accounts.

### 6. Test Your Setup

Run a test campaign to verify everything is working:

```bash
python run.py "Create a 60-second video about summer fitness tips"
```

This will:
1. Generate a script using GPT-4
2. Create voice narration with ElevenLabs
3. Generate video clips with Runway ML
4. Compose the final video with FFmpeg

The output video will be saved in the `output/` directory.

## Troubleshooting

**FFmpeg not found:**
- Ensure FFmpeg is installed and in your system PATH
- Test with: `ffmpeg -version`

**API Key errors:**
- Double-check that all keys are correctly copied to `.env`
- Ensure there are no extra spaces or quotes around the keys

**Module import errors:**
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.8 or higher

**Runway ML authentication issues:**
- Make sure you're using the API key from https://dev.runwayml.com/, not the regular Runway app
- Your account must have credits/subscription for API access

## Next Steps

Once setup is complete, read:
- `README.md` - Project overview and architecture
- `MULTI_ACCOUNT_GUIDE.md` - Managing multiple TikTok accounts
- `ARCHITECTURE.md` - Technical implementation details

## Support

For issues or questions, please open an issue on the GitHub repository.
