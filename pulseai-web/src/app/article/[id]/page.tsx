import { supabase } from '@/lib/supabase'
import Link from 'next/link'
import { ArrowLeft, ExternalLink, Zap } from 'lucide-react'
import { notFound } from 'next/navigation'

export const revalidate = 60

export default async function ArticlePage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params;
  
  // Fetch specific summary + article metadata
  const { data: summary, error } = await supabase
    .from('summaries')
    .select('*, articles(title, url, source, fetched_at)')
    .eq('id', resolvedParams.id)
    .single()

  if (error || !summary) {
    notFound()
  }

  const { articles: article } = summary

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 selection:bg-blue-600 selection:text-white pb-20">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <Zap className="w-5 h-5 text-blue-500 fill-blue-500 group-hover:scale-110 transition-transform" />
            <span className="text-lg font-bold font-sans tracking-tight text-white group-hover:text-blue-400 transition-colors">PulseAI</span>
          </Link>
          <Link href="/" className="flex items-center gap-2 text-sm font-medium text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Daily Pulse
          </Link>
        </div>
      </header>

      {/* Article Content */}
      <article className="max-w-3xl mx-auto px-6 pt-16 mt-8">
        <header className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <span className="px-3 py-1 text-xs font-semibold tracking-wider text-blue-400 bg-blue-400/10 rounded-full">
              {summary.category}
            </span>
            <span className="text-sm font-medium text-slate-500">•</span>
            <span className="text-sm font-medium text-slate-500 uppercase tracking-wider">{article.source}</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight mb-6">
            {article.title}
          </h1>
          <div className="flex items-center text-sm text-slate-400 gap-2">
            <span className="font-semibold text-slate-300">PulseAI Executive Summary</span>
            <span>—</span>
            <time dateTime={summary.edition_date}>
              {new Date(summary.edition_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            </time>
          </div>
        </header>

        <div className="prose prose-invert prose-lg max-w-none text-slate-300">
          <p className="leading-relaxed">
            {summary.summary_text}
          </p>
        </div>

        {/* Action Call */}
        <div className="mt-16 pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-6">
          <a 
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg transition-colors"
          >
            Read Original Article <ExternalLink className="w-4 h-4" />
          </a>
          <p className="text-sm text-slate-500 text-center sm:text-right">
            Sourced via {article.source} at {new Date(article.fetched_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}.
          </p>
        </div>
      </article>
    </main>
  )
}
