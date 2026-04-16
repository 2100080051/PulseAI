import { supabase } from '@/lib/supabase'
import Link from 'next/link'
import { Zap, Clock, ArrowRight } from 'lucide-react'

// Allow incremental static regeneration every 30 seconds for blazing fast SEO
export const revalidate = 30

export default async function Home() {
  // Fetch only approved/edited summaries
  const { data: summaries, error } = await supabase
    .from('summaries')
    .select('*, articles(title, url, source)')
    .in('status', ['approved', 'edited', 'pending']) // User requested maximum SEO volume
    .order('edition_date', { ascending: false })
    .limit(50)

  if (error) {
    console.error('Error fetching summaries:', error)
  }

  // Group by edition date to show the "Daily Pulse" structure
  const groupedByDate = summaries?.reduce((acc: any, summary: any) => {
    const d = summary.edition_date
    if (!acc[d]) acc[d] = []
    acc[d].push(summary)
    return acc
  }, {})

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 selection:bg-blue-600 selection:text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-6 h-6 text-blue-500 fill-blue-500" />
            <span className="text-xl font-bold font-sans tracking-tight text-white">PulseAI</span>
          </div>
          <nav className="hidden sm:flex gap-6 text-sm font-medium text-slate-400">
            <Link href="/" className="hover:text-blue-400 transition-colors">Daily Briefings</Link>
            <Link href="#" className="hover:text-blue-400 transition-colors">Categories</Link>
            <Link href="#" className="hover:text-blue-400 transition-colors">Podcast</Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter mb-6 bg-gradient-to-br from-white to-slate-500 bg-clip-text text-transparent">
          The ultimate pulse <br />on Artificial Intelligence.
        </h1>
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10">
          Professional, jargon-free, AI-generated executive summaries covering the biggest breakthroughs in LLMs, Healthcare, and Tech.
        </p>
      </section>

      {/* Archive Feed */}
      <section className="max-w-4xl mx-auto px-6 pb-24">
        {Object.entries(groupedByDate || {}).map(([dateStr, stories]: [string, any]) => (
          <div key={dateStr} className="mb-16">
            <div className="flex items-center gap-4 mb-8">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-500" />
                {new Date(dateStr).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
              </h2>
              <div className="h-px flex-1 bg-slate-800"></div>
            </div>

            <div className="grid gap-6">
              {stories.map((summary: any) => (
                <Link key={summary.id} href={`/article/${summary.id}`} className="group block">
                  <article className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 transition-colors duration-300">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
                      <div className="flex-1">
                        <span className="inline-block px-3 py-1 text-xs font-semibold tracking-wider text-blue-400 bg-blue-400/10 rounded-full mb-4">
                          {summary.category}
                        </span>
                        <h3 className="text-xl font-bold text-slate-100 group-hover:text-blue-400 transition-colors duration-300 mb-3">
                          {summary.articles?.title}
                        </h3>
                        <p className="text-slate-400 leading-relaxed text-sm md:text-base line-clamp-3">
                          {summary.summary_text}
                        </p>
                      </div>
                      <div className="hidden md:flex flex-col items-end">
                        <span className="text-xs font-medium text-slate-500 uppercase tracking-widest mb-1">Source</span>
                        <span className="text-sm font-semibold text-slate-300">{summary.articles?.source}</span>
                      </div>
                    </div>
                  </article>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </section>
    </main>
  )
}
