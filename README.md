# 🛡️ PostPro - The Reputation Guardian

LinkedIn Post Optimizer that compares your new drafts against your proven history.

## What it does

1. **Upload your LinkedIn data** - Import your Content export (XLSX) to see your top-performing posts
2. **Select your anchor** - Pick a post that performed well as your "DNA template"
3. **Analyze new drafts** - Compare any new post against your winning formula
4. **Get actionable feedback** - Score, risk level, and specific suggestions to improve

## Quick Start (Local)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

### 3. Open in browser

The app will open automatically at `http://localhost:8501`

## Deploy to Streamlit Cloud (Free)

### 1. Push to GitHub

Create a new repository and push these files:
- `app.py`
- `requirements.txt`

### 2. Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Click "Deploy"

### 3. Add your API key

In Streamlit Cloud, go to your app settings → Secrets, and add:

```toml
OPENAI_API_KEY = "sk-your-key-here"
```

Or just enter it in the sidebar each time you use the app.

## How to export your LinkedIn data

1. Go to LinkedIn Settings
2. Click "Get a copy of your data"
3. Select "Posts" 
4. Wait for email (can take up to 24 hours)
5. Download and extract the ZIP
6. Upload the `Content_*.xlsx` file to PostPro

## Tech Stack

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-4o
- **Data Processing**: Pandas

## Author

Built by Nadav Druker

---

PostPro V1.5 - Don't guess. Know.
