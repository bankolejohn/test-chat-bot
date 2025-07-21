# 📋 Heroku Web Deployment Checklist

## ✅ Step 1: Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Repository name: `3mtt-chatbot`
4. Make it public (required for free Heroku deployment)
5. Click "Create repository"

## ✅ Step 2: Upload Files to GitHub
Upload these essential files to your repository:

### Required Files:
- [x] `app.py` - Main Flask application
- [x] `Procfile` - Contains: `web: python app.py`
- [x] `requirements.txt` - Python dependencies
- [x] `runtime.txt` - Contains: `python-3.11.0`
- [x] `knowledge_base.json` - Chatbot knowledge
- [x] `.gitignore` - Ignore unnecessary files

### Optional Files (but recommended):
- [x] `README_DEPLOYMENT.md` - Project documentation
- [x] `training_data.json` - Training examples
- [x] `conversations.json` - Conversation history (will be created)

## ✅ Step 3: Create Heroku Account
1. Go to [heroku.com](https://heroku.com)
2. Click "Sign up"
3. Fill in your details
4. Verify your email address

## ✅ Step 4: Create Heroku App
1. Login to [dashboard.heroku.com](https://dashboard.heroku.com)
2. Click "New" → "Create new app"
3. App name: `your-3mtt-chatbot` (choose unique name)
4. Region: United States or Europe
5. Click "Create app"

## ✅ Step 5: Connect GitHub
1. Go to "Deploy" tab in your Heroku app
2. Select "GitHub" as deployment method
3. Click "Connect to GitHub"
4. Authorize Heroku to access GitHub
5. Search for `3mtt-chatbot` repository
6. Click "Connect"

## ✅ Step 6: Set Environment Variables
1. Go to "Settings" tab
2. Click "Reveal Config Vars"
3. Add these variables:
   ```
   KEY: SECRET_KEY
   VALUE: your-random-secret-key-123456789
   
   KEY: OPENAI_API_KEY  
   VALUE: sk-your-openai-key-here (optional)
   ```

## ✅ Step 7: Deploy
1. Go back to "Deploy" tab
2. Scroll to "Manual deploy" section
3. Select branch: `main`
4. Click "Deploy Branch"
5. Wait for build to complete (2-3 minutes)

## ✅ Step 8: Test Your Chatbot
1. Click "View" button
2. Test with these questions:
   - "What is 3MTT about?"
   - "Why is my dashboard score different?"
   - "What courses do you offer?"

## 🎉 Success!
Your chatbot is now live at: `https://your-app-name.herokuapp.com`

## 📊 Access Admin Features
- Analytics: `https://your-app-name.herokuapp.com/admin/analytics`
- Knowledge Base: `https://your-app-name.herokuapp.com/admin/knowledge`

## 🔧 Troubleshooting
If deployment fails:
1. Check "Activity" tab for error logs
2. Ensure all required files are uploaded
3. Verify environment variables are set
4. Check that `Procfile` contains exactly: `web: python app.py`

## 🔄 Future Updates
To update your chatbot:
1. Make changes to your files
2. Upload to GitHub
3. Go to Heroku "Deploy" tab
4. Click "Deploy Branch" again