# 🌐 Deploy to Heroku via Web Interface (No CLI Required)

## Step 1: Create Heroku Account
1. Go to [heroku.com](https://heroku.com)
2. Sign up for a free account
3. Verify your email

## Step 2: Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Create a new repository called `3mtt-chatbot`
3. Upload all your chatbot files to this repository

## Step 3: Deploy via Heroku Dashboard
1. **Login to Heroku Dashboard**
   - Go to [dashboard.heroku.com](https://dashboard.heroku.com)

2. **Create New App**
   - Click "New" → "Create new app"
   - App name: `your-3mtt-chatbot` (must be unique)
   - Region: Choose your preferred region
   - Click "Create app"

3. **Connect to GitHub**
   - Go to "Deploy" tab
   - Select "GitHub" as deployment method
   - Connect your GitHub account
   - Search for your `3mtt-chatbot` repository
   - Click "Connect"

4. **Set Environment Variables**
   - Go to "Settings" tab
   - Click "Reveal Config Vars"
   - Add these variables:
     ```
     SECRET_KEY = your-random-secret-key-here
     OPENAI_API_KEY = your-openai-key (optional)
     ```

5. **Deploy**
   - Go back to "Deploy" tab
   - Scroll to "Manual deploy"
   - Select "main" branch
   - Click "Deploy Branch"

6. **View Your App**
   - Click "View" button
   - Your chatbot is now live!

## 📋 Files to Upload to GitHub

Make sure these files are in your GitHub repository:
- ✅ `app.py` - Main application
- ✅ `Procfile` - Heroku configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version
- ✅ `knowledge_base.json` - Chatbot knowledge
- ✅ All other project files

## 🔧 Troubleshooting

**If deployment fails:**
1. Check the "Activity" tab for build logs
2. Ensure all files are uploaded to GitHub
3. Verify environment variables are set
4. Check that `Procfile` contains: `web: python app.py`

**Common issues:**
- Missing `Procfile` → Add it with content: `web: python app.py`
- Missing dependencies → Check `requirements.txt`
- Port issues → Already handled in your `app.py`

Your chatbot will be available at:
`https://your-app-name.herokuapp.com`