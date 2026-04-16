import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, Zap, Menu, X } from 'lucide-react'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [searchQ, setSearchQ] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleSearch = useCallback((e) => {
    e.preventDefault()
    if (searchQ.trim().length > 1) {
      navigate(`/search?q=${encodeURIComponent(searchQ.trim())}`)
      setSearchQ('')
      setMobileOpen(false)
    }
  }, [searchQ, navigate])

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      background: scrolled ? 'rgba(5,9,23,0.92)' : 'transparent',
      backdropFilter: scrolled ? 'blur(16px)' : 'none',
      borderBottom: scrolled ? '1px solid rgba(99,102,241,0.12)' : '1px solid transparent',
      transition: 'all 0.3s ease',
    }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', height: 68, gap: 24 }}>

        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 20px rgba(99,102,241,0.4)',
            animation: 'pulse-glow 3s ease-in-out infinite',
          }}>
            <Zap size={18} color="#fff" fill="#fff" />
          </div>
          <span style={{ fontFamily: 'Space Grotesk', fontWeight: 700, fontSize: 20, letterSpacing: '-0.5px' }}>
            Pulse<span style={{ color: '#6366f1' }}>AI</span>
          </span>
        </Link>

        {/* Category links — desktop */}
        <div style={{ display: 'flex', gap: 4, flex: 1, justifyContent: 'center' }} className="nav-links">
          {[
            { label: 'LLMs', slug: 'llms' },
            { label: 'Tools', slug: 'tools' },
            { label: 'Funding', slug: 'funding' },
            { label: 'Healthcare', slug: 'healthcare' },
            { label: 'Policy', slug: 'policy' },
            { label: 'India AI', slug: 'india' },
            { label: 'Research', slug: 'research' },
          ].map(({ label, slug }) => (
            <Link key={slug} to={`/category/${slug}`} style={{
              padding: '6px 12px', borderRadius: 8, fontSize: 13, fontWeight: 500,
              color: 'var(--text-secondary)', transition: 'all 0.2s ease',
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={e => { e.target.style.color = '#fff'; e.target.style.background = 'rgba(99,102,241,0.12)' }}
            onMouseLeave={e => { e.target.style.color = 'var(--text-secondary)'; e.target.style.background = 'transparent' }}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* Search — desktop */}
        <form onSubmit={handleSearch} style={{ display: 'flex', alignItems: 'center', position: 'relative', flexShrink: 0 }}>
          <input
            className="search-input"
            style={{ width: 200, padding: '8px 36px 8px 14px', fontSize: 13 }}
            placeholder="Search AI news…"
            value={searchQ}
            onChange={e => setSearchQ(e.target.value)}
          />
          <button type="submit" style={{ position: 'absolute', right: 10, background: 'none', border: 'none', color: 'var(--text-muted)', padding: 0, display: 'flex' }}>
            <Search size={15} />
          </button>
        </form>

        {/* Mobile toggle */}
        <button
          onClick={() => setMobileOpen(o => !o)}
          style={{ display: 'none', background: 'none', color: 'var(--text-primary)', marginLeft: 'auto' }}
          className="mobile-toggle"
        >
          {mobileOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div style={{
          background: 'rgba(5,9,23,0.98)', borderTop: '1px solid var(--border)',
          padding: '16px 24px 24px', display: 'flex', flexDirection: 'column', gap: 8,
        }}>
          {[
            { label: 'LLMs & Foundation Models', slug: 'llms' },
            { label: 'AI Tools & Products', slug: 'tools' },
            { label: 'Funding & Acquisitions', slug: 'funding' },
            { label: 'AI in Healthcare', slug: 'healthcare' },
            { label: 'AI Policy & Ethics', slug: 'policy' },
            { label: 'India AI', slug: 'india' },
            { label: 'Research & Papers', slug: 'research' },
          ].map(({ label, slug }) => (
            <Link key={slug} to={`/category/${slug}`}
              onClick={() => setMobileOpen(false)}
              style={{ padding: '10px 0', color: 'var(--text-secondary)', fontSize: 15, borderBottom: '1px solid var(--border)' }}
            >{label}</Link>
          ))}
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <input className="search-input" placeholder="Search…" value={searchQ} onChange={e => setSearchQ(e.target.value)} style={{ fontSize: 14 }} />
            <button type="submit" className="btn-primary" style={{ padding: '10px 16px', whiteSpace: 'nowrap' }}>Search</button>
          </form>
        </div>
      )}

      <style>{`
        @media (max-width: 900px) {
          .nav-links { display: none !important; }
          .mobile-toggle { display: flex !important; }
          nav form:not(.mobile-toggle ~ *) { display: none; }
        }
      `}</style>
    </nav>
  )
}
