# Deployment Guide for SHL Assessment Recommender

This guide explains how to deploy both the Python/FastAPI backend and the frontend to a cloud platform. Since the frontend is served as static files by the FastAPI application (`/` serves `static/index.html` and `/static/*` serves styles/scripts), deploying the FastAPI application deploys **both** frontend and backend simultaneously.

---

## Recommended Platform: Render

[Render](https://render.com/) is a cloud platform that offers a free tier for hosting web services and integrates seamlessly with GitHub/GitLab.

### Option 1: Quick Deploy via Render Blueprint (Recommended)

We have created a `render.yaml` configuration file in the project root. This file tells Render exactly how to build and run your service.

1. **Push your code to GitHub / GitLab:**
   Make sure you have committed your files (excluding `.env` and `shl_assessment.db` which are correctly configured in `.gitignore`).
   ```bash
   git init
   git add .
   git commit -m "Prepare deployment files"
   # Push to your remote repo (GitHub/GitLab)
   ```

2. **Connect to Render:**
   - Log in to your [Render Dashboard](https://dashboard.render.com).
   - Click the **New +** button in the top right.
   - Choose **Blueprint**.
   - Connect your GitHub/GitLab repository.

3. **Configure & Deploy:**
   - Select your repository.
   - Render will read the `render.yaml` automatically.
   - It will prompt you for the **`GEMINI_API_KEY`**. Paste your real Gemini API key here.
   - Click **Apply**.
   - Render will build and deploy the app automatically!

---

### Option 2: Manual Deployment on Render

If you prefer to configure the web service manually on the Render dashboard:

1. Click **New +** -> **Web Service**.
2. Connect your repository.
3. Configure the following settings:
   - **Name:** `shl-assessment-recommender`
   - **Region:** Choose the closest region to you.
   - **Branch:** `main` (or whichever branch you are using).
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add **Environment Variables** in the Environment section:
   - `GEMINI_API_KEY` = `your-actual-gemini-api-key`
   - `GEMINI_MODEL` = `gemini-2.5-flash`
   - `DATABASE_URL` = `sqlite+aiosqlite:///./shl_assessment.db` (This configures SQLite)
5. Click **Create Web Service**.

---

## Alternative Platform: Railway

[Railway](https://railway.app/) is another developer-friendly platform with automated builds.

1. Create an account on Railway.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your repository.
4. Click **Variables** on the service page, and add:
   - `PORT` = `8000` (Railway will automatically map incoming traffic)
   - `ANTHROPIC_API_KEY` = `your-actual-api-key`
   - `DATABASE_URL` = `sqlite+aiosqlite:///./shl_assessment.db`
5. Railway will automatically detect the Python project, run `pip install`, and boot the app using your `main.py` or the start command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

---

## Production Considerations

### 1. Database (SQLite)
Currently, the application uses **SQLite** for storing conversational sessions and campaigns. 
- In **Render's Free Tier** (or any serverless platform), the container disk is ephemeral. This means that if the service restarts (which happens once a day or on deployments), the database file (`shl_assessment.db`) will reset, clearing active chats and campaigns.
- **For production use:** Change the `DATABASE_URL` environment variable to a persistent remote database (e.g., PostgreSQL). SQLAlchemy is already set up to be database-agnostic. Example PostgreSQL URL:
  `postgresql+asyncpg://user:password@host:port/database`
  *(Note: You will need to add `asyncpg` to `requirements.txt` if using PostgreSQL).*

### 2. CORS Settings
In `app/main.py`, CORS is configured to allow all origins (`allow_origins=["*"]`). If deploying a sensitive environment, restrict `allow_origins` to your specific custom domain name.
