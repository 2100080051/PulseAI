import { Zap, Code2, Globe2, Mail } from 'lucide-react'
import { Link } from 'react-router-dom'
import { CATEGORIES } from '../lib/supabase'

export default function Footer() {
  return (
    <footer style={{
      borderTop: '1px solid var(--border)',
      background: 'rgba(5,9,23,0.8)',
      padding: '60px 0 32px',
    }}>
      <div className="container">
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 48, marginBottom: 48 }}>

          {/* Brand */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 9,
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Zap size={16} color="#fff" fill="#fff" />
              </div>
              <span style={{ fontFamily: 'Space Grotesk', fontWeight: 700, fontSize: 18 }}>
                Pulse<span style={{ color: '#6366f1' }}>AI</span>
              </span>
            </div>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, maxWidth: 280, marginBottom: 20 }}>
              Your daily pulse on Artificial Intelligence. Automated · Curated · Real-Time AI news for the modern professional.
            </p>
            <div style={{ display: 'flex', gap: 12 }}>
              {[
                { Icon: Globe2, href: 'https://linkedin.com' },
                { Icon: Mail, href: 'https://twitter.com' },
                { Icon: Code2, href: 'https://github.com/2100080051/PulseAI' },
              ].map(({ Icon, href }, i) => (
                <a key={i} href={href} target="_blank" rel="noopener noreferrer" style={{
                  width: 38, height: 38, borderRadius: 10, border: '1px solid var(--border)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--text-muted)', transition: 'all 0.2s ease',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.color = '#6366f1'; e.currentTarget.style.background = 'rgba(99,102,241,0.1)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.background = 'transparent'; }}
                >
                  <Icon size={16} />
                </a>
              ))}
            </div>
          </div>

          {/* Categories */}
          <div>
            <h4 style={{ fontSize: 13, fontWeight: 700, letterSpacing: '1.5px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 16 }}>
              Categories
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {CATEGORIES.map(cat => (
                <Link key={cat.slug} to={`/category/${cat.slug}`} style={{
                  fontSize: 14, color: 'var(--text-secondary)', transition: 'color 0.2s',
                  display: 'flex', alignItems: 'center', gap: 6,
                }}
                onMouseEnter={e => e.currentTarget.style.color = cat.color}
                onMouseLeave={e => e.currentTarget.style.color = 'var(--text-secondary)'}
                >
                  <span>{cat.icon}</span> {cat.name}
                </Link>
              ))}
            </div>
          </div>

          {/* Platform */}
          <div>
            <h4 style={{ fontSize: 13, fontWeight: 700, letterSpacing: '1.5px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 16 }}>
              Platform
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { label: 'Latest Stories', path: '/' },
                { label: 'Search Archive', path: '/search' },
                { label: 'About PulseAI', path: '/#about' },
                { label: 'GitHub', path: 'https://github.com/2100080051/PulseAI', ext: true },
              ].map(({ label, path, ext }) => (
                ext
                  ? <a key={label} href={path} target="_blank" rel="noopener noreferrer" style={{ fontSize: 14, color: 'var(--text-secondary)' }}
                    onMouseEnter={e => e.target.style.color = '#fff'} onMouseLeave={e => e.target.style.color = 'var(--text-secondary)'}>{label}</a>
                  : <Link key={label} to={path} style={{ fontSize: 14, color: 'var(--text-secondary)' }}
                    onMouseEnter={e => e.target.style.color = '#fff'} onMouseLeave={e => e.target.style.color = 'var(--text-secondary)'}>{label}</Link>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div style={{
          paddingTop: 24, borderTop: '1px solid var(--border)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12,
        }}>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            © {new Date().getFullYear()} PulseAI · Built by Nani · April 2026
          </p>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Powered by Groq · Supabase · Llama 3.3 70B
          </p>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          footer > .container > div:first-child { grid-template-columns: 1fr !important; gap: 32px !important; }
        }
      `}</style>
    </footer>
  )
}
