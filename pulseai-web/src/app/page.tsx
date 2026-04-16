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
    <main className="min-h-screen bg-slate-950 text-slate-200 relative overflow-hidden">
      {/* Ambient glowing orb background effect */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-cyan-600/20 blur-[150px] rounded-full pointer-events-none -z-10" />

      {/* Header */}
      <header className="border-b border-white/5 bg-slate-950/60 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg shadow-lg shadow-cyan-500/20">
               <Zap className="w-5 h-5 text-white fill-white" />
            </div>
            <span className="text-2xl font-bold font-outfit tracking-tight text-white">Global Pulse AI</span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 py-24 text-center">
        <h1 className="text-6xl md:text-8xl font-extrabold font-outfit tracking-tighter mb-8 bg-gradient-to-r from-blue-300 via-cyan-200 to-emerald-200 bg-clip-text text-transparent leading-[1.1]">
          The ultimate pulse <br />on Artificial Intelligence.
        </h1>
        <p className="text-lg md:text-xl text-slate-400/90 max-w-2xl mx-auto mb-10 font-medium leading-relaxed">
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
                    className={`block px-5 py-3 rounded-xl text-sm font-semibold transition-all duration-300 border ${isActive ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-[0_0_20px_rgba(6,182,212,0.3)] border-cyan-400/50 scale-[1.02]' : 'bg-slate-900/40 text-slate-400 border-white/5 hover:bg-slate-800/80 hover:text-slate-200 hover:border-white/10'}`}
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
                <div className="grid sm:grid-cols-2 gap-6 mb-12">
                  {data.podcasts.map((pod: any, i: number) => (
                    <div key={i} className="rounded-2xl overflow-hidden bg-slate-900/50 backdrop-blur-sm border border-cyan-500/20 shadow-[0_0_30px_rgba(0,0,0,0.5)] group transition-all duration-500 hover:border-cyan-400/50 hover:shadow-[0_0_40px_rgba(6,182,212,0.15)]">
                      <div className="bg-gradient-to-r from-slate-900 to-slate-800 px-5 py-3 flex items-center justify-between border-b border-white/5">
                        <div className="flex items-center gap-2">
                          <PlayCircle className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
                          <span className="text-sm font-bold font-outfit text-slate-200 tracking-wide capitalize">{pod.name} Update</span>
                        </div>
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                      </div>
                      <video src={pod.url} controls preload="metadata" className="w-full aspect-video object-cover" poster="/api/placeholder/1920/1080" />
                    </div>
                  ))}
                </div>
              )}

              <div className="grid gap-6">
                {data.stories.map((summary: any) => (
                <Link key={summary.id} href={`/article/${summary.id}`} className="group block outline-none">
                  <article className="p-7 rounded-2xl bg-slate-900/40 backdrop-blur-md border border-white/5 hover:border-cyan-500/30 hover:bg-slate-800/60 hover:-translate-y-1 hover:shadow-2xl hover:shadow-cyan-500/10 transition-all duration-400 ease-out h-full flex flex-col justify-between">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-4">
                      <div className="flex-1">
                        <span className="inline-block px-3 py-1 text-xs font-bold tracking-widest uppercase text-cyan-400 bg-cyan-400/10 rounded-full mb-5 border border-cyan-400/20">
                          {summary.category}
                        </span>
                        <h3 className="text-2xl font-bold font-outfit text-slate-100 group-hover:text-cyan-300 transition-colors duration-300 mb-4 leading-snug">
                          {summary.articles?.title}
                        </h3>
                        <p className="text-slate-400/90 leading-relaxed text-sm md:text-[15px] line-clamp-3">
                          {summary.summary_text}
                        </p>
                      </div>
                      <div className="hidden md:flex flex-col items-end shrink-0">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1.5">Source</span>
                        <span className="text-sm font-semibold text-slate-300 bg-slate-800 px-3 py-1 rounded-md">{summary.articles?.source}</span>
                      </div>
                    </div>
                    <div className="flex items-center text-xs font-bold text-cyan-500/0 group-hover:text-cyan-400 transition-all duration-300 pt-4 border-t border-white/5 mt-auto">
                      Read Executive Summary &rarr;
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
