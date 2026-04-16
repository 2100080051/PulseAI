import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Zap, TrendingUp, Globe2, RefreshCw } from 'lucide-react'
import StoryCard from '../components/StoryCard'
import NewsletterSection from '../components/NewsletterSection'
import { fetchLatest, fetchStats, CATEGORIES } from '../lib/supabase'

// ── Animated counter ──────────────────────────────────────────────────────────
function Counter({ target, suffix = '' }) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    if (!target) return
    const step = target / 50
    let cur = 0
    const timer = setInterval(() => {
      cur += step
      if (cur >= target) { setVal(target); clearInterval(timer) }
      else setVal(Math.floor(cur))
    }, 30)
    return () => clearInterval(timer)
  }, [target])
  return <span>{val.toLocaleString()}{suffix}</span>
}

// ── Hero ──────────────────────────────────────────────────────────────────────
function HeroSection({ stats }) {
  return (
    <section style={{ paddingTop: 140, paddingBottom: 80, position: 'relative', overflow: 'hidden' }}>
      {/* Background orbs */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: '10%', left: '5%', width: 500, height: 500, borderRadius: '50%', background: 'radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%)', filter: 'blur(40px)' }} />
        <div style={{ position: 'absolute', top: '20%', right: '5%', width: 400, height: 400, borderRadius: '50%', background: 'radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%)', filter: 'blur(40px)' }} />
        <div style={{ position: 'absolute', bottom: '0%', left: '40%', width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(circle, rgba(6,182,212,0.06) 0%, transparent 70%)', filter: 'blur(40px)' }} />
      </div>

      <div className="container" style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
        {/* Live badge */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', borderRadius: 100, background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)', marginBottom: 28 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981', animation: 'pulse-glow 2s ease-in-out infinite' }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: '#10b981', letterSpacing: '0.5px' }}>Live · Updated Daily</span>
        </div>

        <h1 style={{ fontSize: 'clamp(36px, 7vw, 80px)', fontWeight: 900, lineHeight: 1.08, letterSpacing: '-2px', marginBottom: 24 }}>
          Your Daily Pulse on<br />
          <span className="gradient-text">Artificial Intelligence</span>
        </h1>

        <p style={{ fontSize: 'clamp(16px, 2.5vw, 20px)', color: 'var(--text-secondary)', maxWidth: 600, margin: '0 auto 40px', lineHeight: 1.7 }}>
          AI-curated, human-reviewed news from 15+ trusted sources.
          Delivered every morning to developers, founders, and researchers.
        </p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <a href="#stories" className="btn-primary" style={{ fontSize: 16, padding: '14px 32px' }}>
            Read Today's Edition <ArrowRight size={18} />
          </a>
          <Link to="/search" className="btn-ghost" style={{ fontSize: 16, padding: '14px 32px' }}>
            Search Archive
          </Link>
        </div>

        {/* Stats row */}
        {stats && (
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 60, flexWrap: 'wrap' }}>
            {[
              { value: stats.articles, label: 'Articles Indexed', icon: <TrendingUp size={18} /> },
              { value: stats.summaries, label: 'Stories Published', icon: <Zap size={18} /> },
              { value: stats.sources, label: 'News Sources', icon: <Globe2 size={18} />, suffix: '+' },
              { value: stats.categories, label: 'Categories', icon: <RefreshCw size={18} /> },
            ].map(({ value, label, icon, suffix }) => (
              <div key={label} className="stat-pill">
                <div style={{ color: 'var(--primary)', marginBottom: 6 }}>{icon}</div>
                <div className="number"><Counter target={value} suffix={suffix} /></div>
                <div className="label">{label}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

// ── Category chips ─────────────────────────────────────────────────────────────
function CategoryStrip({ activeSlug, onSelect }) {
  return (
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 32 }}>
      <button
        onClick={() => onSelect(null)}
        style={{
          padding: '7px 18px', borderRadius: 100, fontSize: 13, fontWeight: 600, border: '1px solid',
          borderColor: !activeSlug ? '#6366f1' : 'var(--border)',
          background: !activeSlug ? 'rgba(99,102,241,0.15)' : 'transparent',
          color: !activeSlug ? '#6366f1' : 'var(--text-secondary)',
          cursor: 'pointer', transition: 'all 0.2s',
        }}
      >All</button>
      {CATEGORIES.map(cat => (
        <button
          key={cat.slug}
          onClick={() => onSelect(cat)}
          style={{
            padding: '7px 18px', borderRadius: 100, fontSize: 13, fontWeight: 600, border: '1px solid',
            borderColor: activeSlug === cat.slug ? cat.color : 'var(--border)',
            background: activeSlug === cat.slug ? `${cat.color}18` : 'transparent',
            color: activeSlug === cat.slug ? cat.color : 'var(--text-secondary)',
            cursor: 'pointer', transition: 'all 0.2s',
          }}
        >
          {cat.icon} {cat.name}
        </button>
      ))}
    </div>
  )
}

// ── Home Page ──────────────────────────────────────────────────────────────────
export default function HomePage() {
  const [stories, setStories] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeCat, setActiveCat] = useState(null)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)

  useEffect(() => {
    fetchStats().then(setStats).catch(console.error)
  }, [])

  useEffect(() => {
    setLoading(true)
    setStories([])
    setPage(1)
    fetchLatest({ limit: 12, category: activeCat?.name || null })
      .then(data => { setStories(data); setHasMore(data.length === 12) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [activeCat])

  function loadMore() {
    const nextPage = page + 1
    setPage(nextPage)
    fetchLatest({ limit: 12, category: activeCat?.name || null, page: nextPage })
      .then(data => { setStories(prev => [...prev, ...data]); setHasMore(data.length === 12) })
      .catch(console.error)
  }

  return (
    <>
      <HeroSection stats={stats} />

      <section id="stories" style={{ padding: '24px 0 80px' }}>
        <div className="container">
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
            <div>
              <p className="section-eyebrow">Today's Edition</p>
              <h2 style={{ fontSize: 'clamp(24px, 4vw, 36px)', fontWeight: 800 }}>
                {activeCat ? activeCat.name : 'Latest AI Stories'}
              </h2>
            </div>
          </div>

          <CategoryStrip activeSlug={activeCat?.slug} onSelect={setActiveCat} />

          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '80px 0' }}>
              <div className="spinner" />
            </div>
          ) : stories.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🤖</div>
              <p>No stories yet — run the pipeline and approve some summaries!</p>
            </div>
          ) : (
            <>
              <div className="stories-grid">
                {stories.map((s, i) => <StoryCard key={s.id} summary={s} index={i} />)}
              </div>
              {hasMore && (
                <div style={{ textAlign: 'center', marginTop: 48 }}>
                  <button className="btn-ghost" onClick={loadMore} style={{ fontSize: 15 }}>
                    Load More Stories <ArrowRight size={16} />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </section>

      {/* Category showcase */}
      <section style={{ padding: '0 0 80px' }}>
        <div className="container">
          <p className="section-eyebrow" style={{ marginBottom: 8 }}>Browse by Topic</p>
          <h2 style={{ fontSize: 'clamp(22px, 4vw, 32px)', fontWeight: 800, marginBottom: 32 }}>Explore All Categories</h2>
          <div className="categories-grid">
            {CATEGORIES.map(cat => (
              <Link key={cat.slug} to={`/category/${cat.slug}`} className="cat-card"
                style={{ borderTopColor: cat.color, borderTopWidth: 3 }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = cat.color; e.currentTarget.style.boxShadow = `0 20px 40px rgba(0,0,0,0.3), 0 0 0 1px ${cat.color}40`; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.borderTopColor = cat.color; e.currentTarget.style.boxShadow = 'none'; }}
              >
                <div className="cat-icon">{cat.icon}</div>
                <div className="cat-name" style={{ color: cat.color }}>{cat.name}</div>
                <div className="cat-count">Browse stories →</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <NewsletterSection />
    </>
  )
}
