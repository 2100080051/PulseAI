import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Search, ArrowLeft } from 'lucide-react'
import StoryCard from '../components/StoryCard'
import { searchSummaries } from '../lib/supabase'

function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debouncedValue
}

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialQ = searchParams.get('q') || ''
  const [query, setQuery] = useState(initialQ)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const debouncedQ = useDebounce(query, 400)

  const doSearch = useCallback(async (q) => {
    if (q.trim().length < 2) { setResults([]); setSearched(false); return }
    setLoading(true)
    setSearched(true)
    setSearchParams({ q })
    try {
      const data = await searchSummaries(q.trim())
      setResults(data)
    } catch (e) {
      console.error(e)
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [setSearchParams])

  useEffect(() => { doSearch(debouncedQ) }, [debouncedQ, doSearch])

  // Run initial search if URL has ?q=
  useEffect(() => { if (initialQ) doSearch(initialQ) }, [])

  return (
    <>
      {/* Search hero */}
      <section style={{ paddingTop: 120, paddingBottom: 60, position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.12) 0%, transparent 60%)', pointerEvents: 'none' }} />
        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 14, color: 'var(--text-muted)', marginBottom: 24 }}
            onMouseEnter={e => e.currentTarget.style.color = '#fff'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
          >
            <ArrowLeft size={15} /> Back to Stories
          </Link>

          <p className="section-eyebrow" style={{ marginBottom: 8 }}>Search Archive</p>
          <h1 style={{ fontSize: 'clamp(28px, 5vw, 48px)', fontWeight: 800, marginBottom: 32 }}>
            Find Any <span className="gradient-text">AI Story</span>
          </h1>

          {/* Big search box */}
          <div style={{ position: 'relative', maxWidth: 640 }}>
            <Search size={20} style={{ position: 'absolute', left: 18, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              id="main-search"
              type="text"
              className="search-input"
              style={{ paddingLeft: 52, paddingRight: 20, fontSize: 17, height: 58, borderRadius: 16 }}
              placeholder="e.g. GPT-5, Groq, India AI policy, OpenAI funding…"
              value={query}
              onChange={e => setQuery(e.target.value)}
              autoFocus
            />
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 12 }}>
            Full-text search across all approved AI stories
          </p>
        </div>
      </section>

      {/* Results */}
      <section style={{ padding: '0 0 100px' }}>
        <div className="container">
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 80 }}>
              <div className="spinner" />
            </div>
          ) : !searched ? (
            <div className="empty-state" style={{ padding: '40px 0' }}>
              <div className="empty-icon" style={{ fontSize: 40 }}>🔍</div>
              <p>Start typing to search through all AI stories…</p>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center', marginTop: 24 }}>
                {['OpenAI', 'Groq', 'India AI', 'LLM', 'Funding', 'Llama'].map(term => (
                  <button key={term} onClick={() => setQuery(term)} style={{
                    padding: '7px 18px', borderRadius: 100, fontSize: 13, fontWeight: 600,
                    background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)',
                    color: '#6366f1', cursor: 'pointer', transition: 'all 0.2s',
                  }}>
                    {term}
                  </button>
                ))}
              </div>
            </div>
          ) : results.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">😕</div>
              <p>No stories found for "<strong style={{ color: '#fff' }}>{query}</strong>"</p>
              <p style={{ marginTop: 8, fontSize: 14 }}>Try different keywords or browse by category.</p>
            </div>
          ) : (
            <>
              <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 24 }}>
                <strong style={{ color: '#fff' }}>{results.length}</strong> results for "{query}"
              </p>
              <div className="stories-grid">
                {results.map((s, i) => <StoryCard key={s.id} summary={s} index={i} />)}
              </div>
            </>
          )}
        </div>
      </section>
    </>
  )
}
