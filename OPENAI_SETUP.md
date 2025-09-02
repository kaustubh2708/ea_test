# 🤖 OpenAI API Setup Guide

## 🎯 Overview

To enable 70-word AI-powered email summaries, you need to set up an OpenAI API key.

## 📝 Steps to Get OpenAI API Key

### 1. Create OpenAI Account
1. Go to [https://platform.openai.com](https://platform.openai.com)
2. Sign up or log in to your account
3. Add payment method (required for API access)

### 2. Generate API Key
1. Navigate to [API Keys page](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Give it a name (e.g., "Momo Assistant")
4. Copy the generated key (starts with `sk-`)

### 3. Update Your .env File
1. Open your `.env` file in the project directory
2. Replace the placeholder with your real API key:

```bash
# Before (placeholder)
OPENAI_API_KEY=your_openai_api_key_here

# After (your real key)
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### 4. Restart the Application
```bash
python web_app.py
```

## 💰 Pricing Information

- **Model Used**: GPT-3.5-turbo
- **Cost per Summary**: ~$0.0001 (very cheap!)
- **Monthly Estimate**: $1-5 for typical usage
- **Free Tier**: $5 credit for new accounts

## ✅ Verification

Once set up, you'll see:
- ✅ "OpenAI client initialized for email summarization" in logs
- 🤖 "AI Generated" badge in summaries
- Word count display (≤70 words)

## 🔄 Fallback System

If OpenAI is not available:
- ✅ Automatic fallback to smart analysis
- 📊 "Smart Analysis" badge shown
- Still generates concise summaries

## 🛠️ Troubleshooting

### Common Issues:

**"OpenAI API key not found"**
- Check your `.env` file exists
- Verify the key starts with `sk-`
- Restart the application

**"Incorrect API key provided"**
- Generate a new API key
- Check for extra spaces in `.env` file
- Ensure you have billing set up

**"Rate limit exceeded"**
- You're making too many requests
- Wait a few minutes and try again
- Consider upgrading your OpenAI plan

## 🔐 Security Notes

- ✅ API key is stored locally only
- ✅ Email content is not stored by OpenAI
- ✅ Summaries are generated on-demand
- ✅ No personal data is retained

## 📊 What You Get

With OpenAI enabled:
- 🎯 **Precise 70-word summaries**
- 🧠 **Intelligent content analysis**
- 📋 **Action item extraction**
- ⚡ **Fast processing**
- 🎨 **Professional formatting**

---

**Ready to get smarter email summaries!** 🚀