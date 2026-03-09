MULTI_ACCOUNT_GUIDE.md# 🎯 Multi-Account TikTok Strategy Guide

## Strategy Overview

This system is designed to run **multiple niche-focused TikTok accounts** using the same pipeline with different content profiles.

## 📊 Recommended Setup: 3 Niche Accounts

### Account 1: Startup Growth Hacks (@StartupGrowthHacks)
- **Niche**: Business tips, startup strategies, entrepreneurship
- **Voice**: Rachel (Professional female)
- **Visual Style**: Modern office, professional environment
- **Posting**: 3x daily (9 AM, 2 PM, 7 PM CET)
- **Topics**: Fundraising, growth hacking, product-market fit, scaling

### Account 2: Tech Insider Daily (@TechInsiderDaily)
- **Niche**: Tech trends, product reviews, innovation
- **Voice**: Adam (Enthusiastic male)
- **Visual Style**: Futuristic tech, sleek gadgets, neon aesthetic  
- **Posting**: 3x daily (11 AM, 4 PM, 9 PM CET)
- **Topics**: iPhone features, AI tools, tech comparisons, future trends

### Account 3: Money Mindset Pro (@MoneyMindsetPro)
- **Niche**: Personal finance, investing, wealth-building
- **Voice**: Antoni (Confident male)
- **Visual Style**: Luxury office, financial charts
- **Posting**: 3x daily (8 AM, 1 PM, 6 PM CET)
- **Topics**: Passive income, investing tips, money mistakes, side hustles

## 🚀 Usage Examples

### For Startup Account:
```bash
python run.py "Why most founders fail at product-market fit"
python run.py "3 growth hacking tricks that got us to 100K users"
python run.py "How to raise $1M without giving up equity"
```

### For Tech Account:
```bash
python run.py "iPhone 18 Pro hidden features nobody knows about"
python run.py "5 AI tools that will replace your job in 2026"
python run.py "Why Apple Vision Pro failed (and what's next)"
```

### For Finance Account:
```bash
python run.py "3 passive income streams that actually work"
python run.py "How I turned $1000 into $10000 in 6 months"
python run.py "Money mistakes that keep you poor"
```

## 📝 Content Profiles Configuration

The system uses `content_profiles.json` to manage different content styles:

- **Voice settings**: Each profile has different voice characteristics
- **Visual style**: Runway ML generates visuals matching the niche aesthetic
- **Duration**: Videos optimized for each niche (30-45 seconds)
- **Tone**: Professional, excited, confident - tailored to audience

## 🎨 Why Niche Accounts Work Better

✅ **TikTok Algorithm**: Loves consistency, pushes to relevant audiences
✅ **Higher Engagement**: Followers know what to expect
✅ **Faster Growth**: Algorithm identifies target audience quickly
✅ **Better Monetization**: Brands prefer niche-specific creators
✅ **Authority Building**: You become "the expert" in that topic

## ❌ Why Mixed Content Doesn't Work

- Slower algorithm traction
- Lower engagement per video
- Confused audience
- Harder to monetize
- No clear brand identity

## 🔄 Daily Workflow for 3 Accounts

**Morning (7-10 AM):**
1. Run pipeline for Money Mindset Pro (8 AM post)
2. Run pipeline for Startup Growth Hacks (9 AM post)
3. Run pipeline for Tech Insider Daily (11 AM post)

**Afternoon (12-3 PM):**
1. Run pipeline for Money Mindset Pro (1 PM post)
2. Run pipeline for Startup Growth Hacks (2 PM post)
3. Run pipeline for Tech Insider Daily (4 PM post)

**Evening (6-9 PM):**
1. Run pipeline for Money Mindset Pro (6 PM post)
2. Run pipeline for Startup Growth Hacks (7 PM post)
3. Run pipeline for Tech Insider Daily (9 PM post)

**Result**: 9 high-quality videos per day across 3 accounts

## 💡 Pro Tips

1. **Batch Production**: Generate 3-7 days of content at once
2. **Use Scheduling Tools**: Post automatically at optimal times
3. **Monitor Analytics**: Track which topics perform best per account
4. **A/B Testing**: Test different hooks, styles, durations
5. **Cross-Pollination**: Sometimes share similar topics with different angles

## 📈 Growth Strategy

**Month 1-2**: Focus on consistency (3x daily per account)
**Month 3-4**: Optimize based on analytics, double down on winners
**Month 5-6**: Start monetization, brand deals, affiliate links

## 🎬 Next Steps

1. Clone this repository
2. Set up API keys in `.env`
3. Review `content_profiles.json` and customize
4. Start with 1-2 accounts, add more as you scale
5. Use the pipeline to generate content daily

Good luck building your TikTok empire! 🚀
