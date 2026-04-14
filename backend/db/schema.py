"""
PulseAI — Supabase Database Schema
Run this SQL in your Supabase SQL Editor to create all tables.
"""

SCHEMA_SQL = """
-- ============================================================
-- PulseAI Database Schema
-- Run this entire block in Supabase → SQL Editor → New Query
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLE: articles (raw fetched articles)
-- ============================================================
CREATE TABLE IF NOT EXISTS articles (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url_hash    TEXT UNIQUE NOT NULL,       -- SHA256 of article URL (dedup key)
    title       TEXT NOT NULL,
    url         TEXT NOT NULL,
    source      TEXT NOT NULL,
    raw_content TEXT,
    category    TEXT NOT NULL DEFAULT 'AI Tools & Products',
    fetched_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast dedup checks
CREATE INDEX IF NOT EXISTS idx_articles_url_hash ON articles(url_hash);
CREATE INDEX IF NOT EXISTS idx_articles_fetched_at ON articles(fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);

-- ============================================================
-- TABLE: summaries (AI-generated summaries)
-- ============================================================
CREATE TABLE IF NOT EXISTS summaries (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id      UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    summary_text    TEXT NOT NULL,
    category        TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | rejected | edited
    edition_date    DATE,                             -- which edition it belongs to
    display_order   INTEGER DEFAULT 0,                -- ordering within edition
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_summaries_status ON summaries(status);
CREATE INDEX IF NOT EXISTS idx_summaries_edition_date ON summaries(edition_date DESC);
CREATE INDEX IF NOT EXISTS idx_summaries_article_id ON summaries(article_id);

-- ============================================================
-- TABLE: editions (daily published editions)
-- ============================================================
CREATE TABLE IF NOT EXISTS editions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    edition_date    DATE UNIQUE NOT NULL,
    headline        TEXT,                             -- optional custom headline
    top_stories     UUID[] DEFAULT '{}',              -- ordered array of summary IDs
    status          TEXT NOT NULL DEFAULT 'draft',    -- draft | published
    published_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_editions_date ON editions(edition_date DESC);

-- ============================================================
-- TABLE: subscribers (email subscriber list)
-- ============================================================
CREATE TABLE IF NOT EXISTS subscribers (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           TEXT UNIQUE NOT NULL,
    platform        TEXT DEFAULT 'web',               -- web | linkedin | manual
    is_active       BOOLEAN DEFAULT TRUE,
    subscribed_at   TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
CREATE INDEX IF NOT EXISTS idx_subscribers_active ON subscribers(is_active);

-- ============================================================
-- Full-Text Search on summaries (Supabase built-in)
-- ============================================================
ALTER TABLE summaries ADD COLUMN IF NOT EXISTS fts tsvector
    GENERATED ALWAYS AS (to_tsvector('english', summary_text)) STORED;

ALTER TABLE articles ADD COLUMN IF NOT EXISTS fts tsvector
    GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || COALESCE(raw_content, ''))) STORED;

CREATE INDEX IF NOT EXISTS idx_summaries_fts ON summaries USING gin(fts);
CREATE INDEX IF NOT EXISTS idx_articles_fts ON articles USING gin(fts);

-- ============================================================
-- ROW LEVEL SECURITY (basic — allow all for service role)
-- ============================================================
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE editions ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;

-- Allow service role full access (backend uses service key)
CREATE POLICY "Service role full access" ON articles FOR ALL USING (true);
CREATE POLICY "Service role full access" ON summaries FOR ALL USING (true);
CREATE POLICY "Service role full access" ON editions FOR ALL USING (true);
CREATE POLICY "Service role full access" ON subscribers FOR ALL USING (true);
"""

if __name__ == "__main__":
    print(SCHEMA_SQL)
    print("\n✅ Copy the SQL above and run it in Supabase → SQL Editor → New Query")
