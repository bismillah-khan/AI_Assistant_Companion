# Free Groq API Setup

## Get Your Free API Key (Takes 2 minutes)

1. **Go to Groq Console**: https://console.groq.com/
2. **Sign up** with Google/GitHub (completely free, no credit card needed)
3. **Create API Key**:
   - Click on "API Keys" in the left sidebar
   - Click "Create API Key"
   - Copy the key (starts with `gsk_`)

4. **Update your .env file**:
   - Open `backend/.env`
   - Replace `gsk_free_get_from_groq_console` with your actual key
   - Example: `LLM_API_KEY="gsk_abc123yourkey456def"`

## Why Groq?

- ✅ **100% Free** - Generous free tier, no credit card required
- ✅ **Super Fast** - Fastest inference in the industry
- ✅ **Reliable** - Better JSON following than many models
- ✅ **Good Models** - Llama 3.3 70B, Mixtral, and more

## Available Free Models

You can change `LLM_MODEL` in your .env to any of these:

- `llama-3.3-70b-versatile` (default, best for general tasks)
- `llama-3.1-70b-versatile` (very capable)
- `mixtral-8x7b-32768` (good for long context)
- `gemma2-9b-it` (fast and efficient)

## Limits

Free tier includes:
- 14,400 requests per day
- 30 requests per minute
- More than enough for personal use!

## Next Steps

After updating your API key in `.env`, restart the backend:
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then test your chat at: http://localhost:5173
