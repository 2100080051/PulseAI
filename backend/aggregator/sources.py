"""
PulseAI — RSS Feed Sources
All trusted AI news RSS feeds for aggregation.
"""

RSS_FEEDS = [
    # === Global AI Labs ===
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "category": "LLMs & Foundation Models",
    },
    {
        "name": "Anthropic Blog",
        "url": "https://www.anthropic.com/rss.xml",
        "category": "LLMs & Foundation Models",
    },
    {
        "name": "Google DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "category": "LLMs & Foundation Models",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "category": "Research & Papers",
    },
    # === Tech Media ===
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "AI Tools & Products",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "category": "AI Tools & Products",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "category": "AI Tools & Products",
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/feed/",
        "category": "Research & Papers",
    },
    {
        "name": "Wired AI",
        "url": "https://www.wired.com/feed/category/artificial-intelligence/latest/rss",
        "category": "AI Tools & Products",
    },
    # === Research ===
    {
        "name": "ArXiv AI (cs.AI)",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "category": "Research & Papers",
    },
    {
        "name": "ArXiv ML (cs.LG)",
        "url": "https://rss.arxiv.org/rss/cs.LG",
        "category": "Research & Papers",
    },
    # === India AI ===
    {
        "name": "Analytics India Magazine",
        "url": "https://analyticsindiamag.com/feed/",
        "category": "India AI",
    },
    {
        "name": "Inc42 Tech",
        "url": "https://inc42.com/feed/",
        "category": "India AI",
    },
    # === Policy & Ethics ===
    {
        "name": "AI Now Institute",
        "url": "https://ainowinstitute.org/feed",
        "category": "AI Policy & Ethics",
    },
    # === Funding ===
    {
        "name": "TechCrunch Startups",
        "url": "https://techcrunch.com/category/startups/feed/",
        "category": "Funding & Acquisitions",
    },
    # === Macro & World ===
    {
        "name": "Reuters World News",
        "url": "https://www.reutersagency.com/feed/?best-topics=world-news&type=rss",
        "category": "Geopolitics",
    },
    {
        "name": "CNBC Tech",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910",
        "category": "Technical News (World)",
    },
    {
        "name": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rssindex",
        "category": "Share Market (World)",
    },
    {
        "name": "Moneycontrol Markets",
        "url": "https://www.moneycontrol.com/rss/marketreports.xml",
        "category": "Share Market (India)",
    },
]

# === NewsAPI Queries ===
NEWSAPI_QUERIES = [
    {"q": "artificial intelligence", "category": "AI Tools & Products"},
    {"q": "large language model OR LLM", "category": "LLMs & Foundation Models"},
    {"q": "AI funding startup", "category": "Funding & Acquisitions"},
    {"q": "AI healthcare", "category": "AI in Healthcare"},
    {"q": "AI regulation policy", "category": "AI Policy & Ethics"},
    {"q": "India AI technology", "category": "India AI"},
    {"q": "machine learning research", "category": "Research & Papers"},
    {"q": "global geopolitics OR foreign affairs", "category": "Geopolitics"},
    {"q": "technology news silicon valley", "category": "Technical News (World)"},
    {"q": "stock market OR wall street", "category": "Share Market (World)"},
    {"q": "nse bse share market india", "category": "Share Market (India)"},
]
