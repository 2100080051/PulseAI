# ⚡ PulseAI — Daily AI News Platform

> *Your daily pulse on Artificial Intelligence*

Automated · Curated · Real-Time | Built by Nani · April 2026

---

## 🏗️ Project Structure

```
pulseai/
├── backend/
│   ├── aggregator/
│   │   ├── sources.py        # RSS feeds + NewsAPI queries config
│   │   └── fetcher.py        # Aggregation pipeline
│   ├── ai/
│   │   └── summarizer.py     # LangChain + Groq summarization
│   └── db/
│       ├── client.py         # Supabase client singleton
│       └── schema.py         # SQL schema (run in Supabase)
├── dashboard/
│   └── app.py                # Streamlit editorial dashboard
├── scheduler/
│   └── cron.py               # APScheduler daily runner
├── .env                      # Your API keys (never commit this)
├── .env.example              # Template for .env
├── requirements.txt
└── README.md
```

---

## 🚀 Setup Guide

### Step 1 — Clone & Install Dependencies
```bash
git clone https://github.com/2100080051/PulseAI.git
cd PulseAI
pip install -r requirements.txt
```

### Step 2 — Configure Environment
Copy `.env.example` to `.env` (already done if you're using this repo).
Your `.env` already has `NEWS_API_KEY` and `GROQ_API_KEY` set.

### Step 3 — Set Up Supabase ⚡
👉 See the **Supabase Setup Guide** below.

### Step 4 — Test the Pipeline
```bash
# Test aggregator only (no Supabase needed yet — just check fetching)
python -m backend.aggregator.fetcher

# Run full pipeline manually
python scheduler/cron.py --run-now
```

### Step 5 — Launch Editorial Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 🗄️ Supabase Setup Guide

### 1. Create Account & Project
1. Go to **https://supabase.com**
2. Sign up (free) → Create New Project
3. Name it `pulseai` → Set a strong DB password → Select region: `Southeast Asia (Singapore)`
4. Wait ~2 minutes for project to provision

### 2. Get API Keys
1. Go to **Project Settings → API**
2. Copy:
   - `Project URL` → paste as `SUPABASE_URL` in `.env`
   - `anon public` key → paste as `SUPABASE_ANON_KEY` in `.env`
   - `service_role` key → paste as `SUPABASE_SERVICE_KEY` in `.env`

### 3. Create Database Schema
1. Go to **SQL Editor → New Query**
2. Run `python backend/db/schema.py` to print the SQL
3. Copy the SQL output and paste it into Supabase SQL Editor
4. Click **Run** → you should see "Success. No rows returned."

### 4. Verify Tables
Go to **Table Editor** — you should see:
- `articles`
- `summaries`
- `editions`
- `subscribers`

---

## ⚡ Daily Workflow

```
6:00 AM IST → Scheduler runs aggregator
            → RSS + NewsAPI fetch new articles
            → Groq LLM summarizes each article
            → Stored in Supabase as "pending"

~6:20 AM    → Founder opens dashboard (streamlit run dashboard/app.py)
            → Reviews AI summaries (20–30 min)
            → Approves / edits / rejects

~7:00 AM    → Export LinkedIn newsletter draft from dashboard
            → Post to LinkedIn
```

---

## 🔧 Run Commands

| Command | Purpose |
|---------|---------|
| `streamlit run dashboard/app.py` | Launch editorial dashboard |
| `python scheduler/cron.py --run-now` | Run full pipeline immediately |
| `python scheduler/cron.py` | Start scheduled (6 AM IST daily) |
| `python -m backend.aggregator.fetcher` | Test aggregator only |
| `python -m backend.ai.summarizer` | Test summarizer only |

---

## 📊 Tech Stack

| Layer | Tech | Cost |
|-------|------|------|
| Aggregation | feedparser + NewsAPI | Free |
| AI | Groq API + Llama 3.3 70B | ~₹0 |
| Pipeline | LangChain | Free |
| Database | Supabase (PostgreSQL) | Free tier |
| Dashboard | Streamlit | Free |
| Scheduling | APScheduler | Free |

---

*PulseAI — Built by Nani | April 2026 | Confidential*
