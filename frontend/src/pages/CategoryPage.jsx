import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import StoryCard from '../components/StoryCard'
import NewsletterSection from '../components/NewsletterSection'
import { fetchLatest, getCategoryBySlug, CATEGORIES } from '../lib/supabase'

export default function CategoryPage() {
  const { slug } = useParams()
  const cat = getCategoryBySlug(slug)
  const [stories, setStories] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)

  useEffect(() => {
    if (!cat) return
    setLoading(true)
    setStories([])
    setPage(1)
    fetchLatest({ limit: 12, category: cat.name })
      .then(data => { setStories(data); setHasMore(data.length === 12) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [slug])

  function loadMore() {
    const next = page + 1
    setPage(next)
    fetchLatest({ limit: 12, category: cat?.name, page: next })
      .then(data => { setStories(prev => [...prev, ...data]); setHasMore(data.length === 12) })
  }

  if (!cat) return (
    <div style={{ paddingTop: 120, textAlign: 'center' }}>
      <p style={{ fontSize: 18, color: 'var(--text-muted)' }}>Category not found.</p>
      <Link to="/" className="btn-primary" style={{ marginTop: 20, display: 'inline-flex' }}>Go Home</Link>
    </div>
  )

  return (
    <>
      {/* Category hero */}
      <section style={{ paddingTop: 120, paddingBottom: 60, position: 'relative', overflow: 'hidden' }}>
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none',
          background: `radial-gradient(ellipse at 50% 0%, ${cat.color}18 0%, transparent 60%)`,
        }} />
        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 14, color: 'var(--text-muted)', marginBottom: 24, transition: 'color 0.2s' }}
            onMouseEnter={e => e.currentTarget.style.color = '#fff'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
          >
            <ArrowLeft size={15} /> Back to All Stories
          </Link>

          <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 16 }}>
            <div style={{
              width: 64, height: 64, borderRadius: 18, fontSize: 28,
              background: `${cat.color}18`, border: `1px solid ${cat.color}40`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {cat.icon}
            </div>
            <div>
              <p className="section-eyebrow" style={{ color: cat.color }}>Category</p>
              <h1 style={{ fontSize: 'clamp(28px, 5vw, 48px)', fontWeight: 800, lineHeight: 1.1 }}>{cat.name}</h1>
            </div>
          </div>

          {/* Other category chips */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 24 }}>
            {CATEGORIES.filter(c => c.slug !== slug).map(c => (
              <Link key={c.slug} to={`/category/${c.slug}`} style={{
                padding: '6px 14px', borderRadius: 100, fontSize: 12, fontWeight: 600,
                background: `${c.color}12`, border: `1px solid ${c.color}30`, color: c.color,
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = `${c.color}25`; }}
              onMouseLeave={e => { e.currentTarget.style.background = `${c.color}12`; }}
              >{c.icon} {c.name}</Link>
            ))}
          </div>
        </div>
      </section>

      {/* Stories */}
      <section style={{ padding: '0 0 80px' }}>
        <div className="container">
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 80 }}>
              <div className="spinner" />
            </div>
          ) : stories.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">{cat.icon}</div>
              <p>No stories in this category yet. Check back after the next pipeline run.</p>
            </div>
          ) : (
            <>
              <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 24 }}>{stories.length} stories found</p>
              <div className="stories-grid">
                {stories.map((s, i) => <StoryCard key={s.id} summary={s} index={i} />)}
              </div>
              {hasMore && (
                <div style={{ textAlign: 'center', marginTop: 48 }}>
                  <button className="btn-ghost" onClick={loadMore}>
                    Load More <ArrowRight size={16} />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </section>

      <NewsletterSection />
    </>
  )
}
