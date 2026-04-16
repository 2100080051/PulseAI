const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

// ── Data helpers ──────────────────────────────────────────────────────────────

export const CATEGORIES = [
  { name: 'LLMs & Foundation Models', slug: 'llms', color: '#6366f1', icon: '🧠' },
  { name: 'AI Tools & Products',      slug: 'tools', color: '#06b6d4', icon: '🛠️' },
  { name: 'Funding & Acquisitions',   slug: 'funding', color: '#10b981', icon: '💰' },
  { name: 'AI in Healthcare',          slug: 'healthcare', color: '#f59e0b', icon: '🏥' },
  { name: 'AI Policy & Ethics',        slug: 'policy', color: '#ef4444', icon: '⚖️' },
  { name: 'India AI',                  slug: 'india', color: '#f97316', icon: '🇮🇳' },
  { name: 'Research & Papers',         slug: 'research', color: '#8b5cf6', icon: '📄' },
  { name: 'Technical News (World)',    slug: 'tech-world', color: '#2563eb', icon: '💻' },
  { name: 'Geopolitics',               slug: 'geopolitics', color: '#dc2626', icon: '🌍' },
  { name: 'Share Market (World)',      slug: 'markets-world', color: '#059669', icon: '📈' },
  { name: 'Share Market (India)',      slug: 'markets-india', color: '#ea580c', icon: '🇮🇳📈' },
]

export const getCategoryBySlug = (slug) =>
  CATEGORIES.find((c) => c.slug === slug)

export const getCategoryByName = (name) =>
  CATEGORIES.find((c) => c.name === name) || { color: '#6366f1', icon: '⚡' }

/** Fetch latest approved summaries */
export async function fetchLatest({ limit = 12, category = null, page = 1 } = {}) {
  let url = `${API_URL}/api/summaries?limit=${limit}&page=${page}`
  if (category) url += `&category=${encodeURIComponent(category)}`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch stories')
  const json = await res.json()
  return json.data || []
}

/** Full-text search */
export async function searchSummaries(query) {
  const url = `${API_URL}/api/search?q=${encodeURIComponent(query)}`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Search failed')
  const json = await res.json()
  return json.results || []
}

/** Platform stats */
export async function fetchStats() {
  const res = await fetch(`${API_URL}/api/summaries/stats`)
  if (!res.ok) throw new Error('Stats fetch failed')
  const data = await res.json()
  return { 
    articles: data.total_articles || 0, 
    summaries: data.total_summaries || 0, 
    sources: data.sources || 15, 
    categories: data.categories || 7 
  }
}

/** Subscribe email */
export async function subscribeEmail(email) {
  const res = await fetch(`${API_URL}/api/subscribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, platform: 'web' })
  })
  if (!res.ok) throw new Error('Subscribe failed')
  return res.json()
}
