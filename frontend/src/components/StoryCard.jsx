import { ExternalLink, Clock } from 'lucide-react'
import { getCategoryByName } from '../lib/supabase'

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  const hours = Math.floor(mins / 60)
  const days = Math.floor(hours / 24)
  if (days > 0) return `${days}d ago`
  if (hours > 0) return `${hours}h ago`
  if (mins > 0) return `${mins}m ago`
  return 'Just now'
}

export default function StoryCard({ summary, index = 0 }) {
  const article = summary.articles || {}
  const cat = getCategoryByName(summary.category)

  return (
    <div
      className="story-card"
      style={{ animationDelay: `${index * 60}ms`, opacity: 0 }}
    >
      {/* Category badge + time */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
        <span
          className="cat-badge"
          style={{
            background: `${cat.color}18`,
            color: cat.color,
            border: `1px solid ${cat.color}30`,
          }}
        >
          <span>{cat.icon}</span>
          {summary.category}
        </span>
        <span style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
          <Clock size={11} />
          {timeAgo(summary.created_at)}
        </span>
      </div>

      {/* Image (if available) */}
      {article.image_url && (
        <a href={article.url} target="_blank" rel="noopener noreferrer">
          <div style={{
            width: '100%',
            height: '160px',
            borderRadius: '8px',
            marginBottom: '14px',
            overflow: 'hidden',
          }}>
            <img 
              src={article.image_url} 
              alt={article.title || 'Article image'}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              onError={(e) => e.target.style.display = 'none'}
            />
          </div>
        </a>
      )}

      {/* Title */}
      <h3 style={{
        fontSize: 16,
        fontWeight: 650,
        lineHeight: 1.45,
        color: 'var(--text-primary)',
        marginBottom: 12,
        fontFamily: 'Space Grotesk, Inter, sans-serif',
      }}>
        {article.title || 'AI Story'}
      </h3>

      {/* Summary */}
      <p style={{
        fontSize: 14,
        color: 'var(--text-secondary)',
        lineHeight: 1.7,
        marginBottom: 18,
        display: '-webkit-box',
        WebkitLineClamp: 4,
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
      }}>
        {summary.summary_text}
      </p>

      {/* Footer: source + read more */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto' }}>
        <span style={{
          fontSize: 12, color: 'var(--text-muted)',
          background: 'rgba(255,255,255,0.04)',
          padding: '3px 10px', borderRadius: 100, border: '1px solid var(--border)',
        }}>
          {article.source || 'PulseAI'}
        </span>

        {article.url && (
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'flex', alignItems: 'center', gap: 5, fontSize: 13,
              color: 'var(--primary)', fontWeight: 500, transition: 'gap 0.2s ease',
            }}
            onMouseEnter={e => e.currentTarget.style.gap = '8px'}
            onMouseLeave={e => e.currentTarget.style.gap = '5px'}
          >
            Read more <ExternalLink size={13} />
          </a>
        )}
      </div>
    </div>
  )
}
