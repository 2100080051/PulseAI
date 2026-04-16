import { useState } from 'react'
import { Mail, ArrowRight, Check, Loader } from 'lucide-react'
import { subscribeEmail } from '../lib/supabase'

export default function NewsletterSection() {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | success | error | exists
  const [message, setMessage] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!email.includes('@')) return
    setStatus('loading')
    try {
      const result = await subscribeEmail(email)
      if (result.status === 'already_exists') {
        setStatus('exists')
        setMessage("You're already subscribed! Check your inbox.")
      } else {
        setStatus('success')
        setMessage('Welcome to PulseAI! First edition coming tomorrow. 🎉')
        setEmail('')
      }
    } catch {
      setStatus('error')
      setMessage('Something went wrong. Please try again.')
    }
  }

  return (
    <section style={{ padding: '100px 0' }}>
      <div className="container">
        <div style={{
          position: 'relative', overflow: 'hidden',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(139,92,246,0.08) 50%, rgba(6,182,212,0.06) 100%)',
          border: '1px solid rgba(99,102,241,0.25)',
          borderRadius: 28,
          padding: '64px 48px',
          textAlign: 'center',
        }}>
          {/* Decorative glow blobs */}
          <div style={{
            position: 'absolute', top: -80, left: '20%',
            width: 300, height: 300,
            background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)',
            pointerEvents: 'none',
          }} />
          <div style={{
            position: 'absolute', bottom: -80, right: '20%',
            width: 250, height: 250,
            background: 'radial-gradient(circle, rgba(6,182,212,0.1) 0%, transparent 70%)',
            pointerEvents: 'none',
          }} />

          <div style={{ position: 'relative', zIndex: 1 }}>
            {/* Icon */}
            <div style={{
              width: 64, height: 64, borderRadius: 18,
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 24px',
              boxShadow: '0 8px 32px rgba(99,102,241,0.4)',
            }}>
              <Mail size={28} color="#fff" />
            </div>

            <p className="section-eyebrow" style={{ marginBottom: 12 }}>Stay Ahead</p>
            <h2 style={{ fontSize: 'clamp(28px, 5vw, 44px)', fontWeight: 800, marginBottom: 16, lineHeight: 1.2 }}>
              Get AI News Delivered
              <br />
              <span className="gradient-text">Daily to Your Inbox</span>
            </h2>
            <p style={{ fontSize: 17, color: 'var(--text-secondary)', maxWidth: 500, margin: '0 auto 40px', lineHeight: 1.7 }}>
              Join thousands of AI professionals who start their day with PulseAI.
              Curated, human-reviewed, and always on point.
            </p>

            {/* Form */}
            {status === 'success' || status === 'exists' ? (
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: 10,
                padding: '16px 28px', borderRadius: 14,
                background: status === 'success' ? 'rgba(16,185,129,0.15)' : 'rgba(99,102,241,0.15)',
                border: `1px solid ${status === 'success' ? 'rgba(16,185,129,0.3)' : 'rgba(99,102,241,0.3)'}`,
                color: status === 'success' ? '#10b981' : '#6366f1',
                fontSize: 15, fontWeight: 500,
              }}>
                <Check size={18} />
                {message}
              </div>
            ) : (
              <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 12, maxWidth: 460, margin: '0 auto', justifyContent: 'center' }}>
                <input
                  className="email-input"
                  type="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  disabled={status === 'loading'}
                  id="newsletter-email"
                />
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={status === 'loading'}
                  style={{ flexShrink: 0, opacity: status === 'loading' ? 0.7 : 1 }}
                >
                  {status === 'loading'
                    ? <Loader size={16} style={{ animation: 'spin 0.8s linear infinite' }} />
                    : <><span>Subscribe</span><ArrowRight size={16} /></>
                  }
                </button>
              </form>
            )}

            {status === 'error' && (
              <p style={{ marginTop: 12, color: '#ef4444', fontSize: 14 }}>{message}</p>
            )}

            <p style={{ marginTop: 16, fontSize: 13, color: 'var(--text-muted)' }}>
              Free forever · No spam · Unsubscribe anytime
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
