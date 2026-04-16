import { supabase } from '@/lib/supabase'
import Link from 'next/link'
import { Zap, Clock, PlayCircle } from 'lucide-react'

// Dynamic forced fetch or simple ISR
export const revalidate = 30

const CATEGORIES = [
  "All",
  "LLMs & Foundation Models",
  "AI Tools & Products",
  "Funding & Acquisitions",
  "AI in Healthcare",
  "AI Policy & Ethics",
  "India AI",
  "Research & Papers"
]

export default async function Home({ searchParams }: { searchParams: Promise<{ category?: string }> }) {
  const resolvedParams = await searchParams;
  const currentCategory = resolvedParams.category && resolvedParams.category !== "All" ? resolvedParams.category : null;

  // Fetch only approved/edited summaries
  let query = supabase
    .from('summaries')
    .select('*, articles(title, url, source)')
    .in('status', ['approved', 'edited', 'pending']) 
    .order('edition_date', { ascending: false })
    .limit(50)

  if (currentCategory) {
    query = query.eq('category', currentCategory)
  }

  const { data: summaries, error } = await query;

  if (error) {
    console.error('Error fetching summaries:', error)
  }

  // Fetch available podcasts from the brand new Cloud Storage Bucket!
  const { data: podcastFiles } = await supabase.storage.from('podcasts').list()

  // Group by edition date to show the "Daily Pulse" structure
  const groupedByDate = summaries?.reduce((acc: any, summary: any) => {
    const d = summary.edition_date
    if (!acc[d]) acc[d] = { stories: [], podcasts: [] }
    acc[d].stories.push(summary)
    return acc
  }, {})

  // Map podcast files to their exact dates
  if (podcastFiles) {
    for (const file of podcastFiles) {
      if (!file.name.endsWith('.mp4')) continue;
      // name format: 2026-04-17_morning.mp4
      const [dateStr, editionRaw] = file.name.split('_')
      if (groupedByDate && groupedByDate[dateStr]) {
        const editionType = editionRaw ? editionRaw.replace('.mp4', '') : 'Podcast'
        const publicUrl = supabase.storage.from('podcasts').getPublicUrl(file.name).data.publicUrl
        groupedByDate[dateStr].podcasts.push({
            name: editionType,
            url: publicUrl
        })
      }
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 selection:bg-blue-600 selection:text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-6 h-6 text-blue-500 fill-blue-500" />
            <span className="text-xl font-bold font-sans tracking-tight text-white">Global Pulse AI</span>
          </div>
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

      {/* Archive Feed with Sidebar */}
      <section className="max-w-6xl mx-auto px-6 pb-24 flex flex-col md:flex-row gap-12">
        {/* Category Sidebar */}
        <aside className="w-full md:w-64 shrink-0">
          <div className="sticky top-24">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Categories</h3>
            <div className="flex gap-2 flex-wrap md:flex-col">
              {CATEGORIES.map(cat => {
                const isActive = (!currentCategory && cat === "All") || (currentCategory === cat);
                return (
                  <Link 
                    key={cat} 
                    href={cat === "All" ? "/" : `/?category=${encodeURIComponent(cat)}`}
                    className={`block px-4 py-2 rounded-lg text-sm font-medium transition-all ${isActive ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                  >
                    {cat}
                  </Link>
                )
              })}
            </div>
          </div>
        </aside>

        {/* Stories Timeline */}
        <div className="flex-1">
          {Object.entries(groupedByDate || {}).map(([dateStr, data]: [string, any]) => (
            <div key={dateStr} className="mb-20">
              <div className="flex items-center gap-4 mb-8">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-500" />
                  {new Date(dateStr).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
                </h2>
                <div className="h-px flex-1 bg-slate-800"></div>
              </div>

              {/* Podcasts Section */}
              {data.podcasts.length > 0 && (
                <div className="grid sm:grid-cols-2 gap-4 mb-8">
                  {data.podcasts.map((pod: any, i: number) => (
                    <div key={i} className="rounded-2xl overflow-hidden bg-black border border-slate-800">
                      <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2">
                        <PlayCircle className="w-4 h-4 text-blue-400" />
                        <span className="text-sm font-bold text-slate-300 capitalize">{pod.name} Update</span>
                      </div>
                      <video src={pod.url} controls preload="metadata" className="w-full aspect-video" poster="/api/placeholder/1920/1080" />
                    </div>
                  ))}
                </div>
              )}

              <div className="grid gap-6">
                {data.stories.map((summary: any) => (
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
        </div>
      </section>
    </main>
  )
}
