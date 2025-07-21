# 🚀 3MTT Chatbot Deployment Guide

## Quick Start Options

### 🟢 Option 1: Heroku (Recommended for Beginners)

**Why Heroku?**
- Free tier available
- Easy to use
- Automatic scaling
- Built-in SSL

**Steps:**
1. **Create Heroku Account**: Go to [heroku.com](https://heroku.com) and sign up
2. **Install Heroku CLI**: Download from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Deploy:**
   ```bash
   # Login to Heroku
   heroku login
   
   # Create app
   heroku create your-3mtt-chatbot
   
   # Set environment variables
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set OPENAI_API_KEY=your-openai-key-here
   
   # Initialize git (if not already done)
   git init
   git add .
   git commit -m "Initial commit"
   
   # Deploy
   git push heroku main
   
   # Open your app
   heroku open
   ```

**Your chatbot will be live at**: `https://your-3mtt-chatbot.herokuapp.com`

---

### 🟡 Option 2: Railway (Modern & Fast)

**Why Railway?**
- Modern platform
- Fast deployments
- Good free tier
- Easy environment management

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set environment variables:
   - `SECRET_KEY`: your-secret-key
   - `OPENAI_API_KEY`: your-openai-key
4. Deploy automatically!

---

### 🟠 Option 3: Render (Free Tier)

**Why Render?**
- Generous free tier
- Automatic SSL
- Easy to use
- Good performance

**Steps:**
1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Choose "Web Service"
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`
6. Add environment variables
7. Deploy!

---

### 🔵 Option 4: Embed in Your Existing Website

**For adding chatbot to your current website:**

1. **Deploy your chatbot** using any option above
2. **Get your chatbot URL** (e.g., `https://your-app.herokuapp.com`)
3. **Add the widget code** to your website:

```html
<!-- Add this before closing </body> tag -->
<div id="chatbot-widget" style="position: fixed; bottom: 20px; right: 20px;">
    <iframe 
        src="https://your-chatbot-url.herokuapp.com" 
        width="350" 
        height="500"
        style="border: none; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
    </iframe>
</div>
```

Or use the complete widget from `embed_widget.html` for a more integrated experience.

---

## 🔧 Pre-Deployment Checklist

### ✅ Required Files (Already Created)
- [x] `Procfile` - Tells Heroku how to run your app
- [x] `runtime.txt` - Specifies Python version
- [x] `requirements.txt` - Lists Python dependencies
- [x] `railway.json` - Railway configuration
- [x] `render.yaml` - Render configuration

### ✅ Environment Variables to Set
- `SECRET_KEY` - For Flask sessions (generate a random string)
- `OPENAI_API_KEY` - Your OpenAI API key (optional, works without it)

### ✅ Code Ready for Production
- [x] Debug mode disabled
- [x] Host set to '0.0.0.0'
- [x] Port from environment variable
- [x] Error handling in place

---

## 🌐 Custom Domain Setup

After deployment, you can add your custom domain:

### Heroku Custom Domain
```bash
heroku domains:add www.your-domain.com
heroku domains:add your-domain.com
```

### Railway/Render Custom Domain
- Go to your app settings
- Add custom domain
- Update your DNS records

---

## 📊 Monitoring Your Deployed Chatbot

### View Logs
```bash
# Heroku
heroku logs --tail

# Railway - check dashboard
# Render - check dashboard
```

### Analytics Dashboard
Access at: `https://your-app-url.com/admin/analytics`

### Knowledge Base Management
Access at: `https://your-app-url.com/admin/knowledge`

---

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit API keys to git
2. **HTTPS**: All platforms provide SSL automatically
3. **Secret Key**: Use a strong, random secret key
4. **Admin Routes**: Consider adding authentication for admin routes

---

## 💰 Cost Breakdown

| Platform | Free Tier | Paid Plans |
|----------|-----------|------------|
| Heroku | 550-1000 hours/month | $7+/month |
| Railway | $5 credit/month | $0.000463/GB-hour |
| Render | 750 hours/month | $7+/month |
| DigitalOcean | $200 credit (new users) | $5+/month |

---

## 🚨 Troubleshooting

### Common Issues:

**Port Issues:**
- Make sure your app uses `PORT` environment variable
- Code already handles this: `port = int(os.environ.get('PORT', 5002))`

**Dependencies:**
- Ensure `requirements.txt` is complete
- Run `pip freeze > requirements.txt` to update

**Environment Variables:**
- Set `SECRET_KEY` and `OPENAI_API_KEY` in platform settings
- App works without OpenAI key (uses smart mock responses)

**File Permissions:**
- JSON files are created automatically
- No special permissions needed

---

## 🎉 Next Steps After Deployment

1. **Test your live chatbot** with various questions
2. **Share the URL** with your team/users
3. **Monitor analytics** at `/admin/analytics`
4. **Update knowledge base** at `/admin/knowledge`
5. **Collect user feedback** and improve responses

---

## 📞 Support

If you need help with deployment:
1. Check the platform's documentation
2. Review error logs
3. Ensure all environment variables are set
4. Test locally first with `python app.py`

Your 3MTT chatbot is ready for the world! 🌍