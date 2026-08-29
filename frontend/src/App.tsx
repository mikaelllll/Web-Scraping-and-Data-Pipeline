import { formatDistanceToNow } from 'date-fns'
import { Activity, ArrowUpRight, Database, Layers3, LoaderCircle, Network, Newspaper, Play, Radio, RefreshCw, Search, Server, Sparkles } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { MetricCard } from './components/MetricCard'
import { api, type Dashboard, type Run } from './lib/api'
import './styles.css'

const POLL_MS = 1800

export default function App() {
  const [data, setData] = useState<Dashboard | null>(null)
  const [activeRun, setActiveRun] = useState<Run | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')

  const refresh = useCallback(async () => {
    try { setData(await api.dashboard()); setError(null) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to reach the API') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { void refresh() }, [refresh])
  useEffect(() => {
    if (!activeRun || !['queued', 'running'].includes(activeRun.status)) return
    const timer = window.setInterval(async () => {
      try {
        const run = await api.run(activeRun.id); setActiveRun(run)
        if (run.status === 'completed' || run.status === 'failed') await refresh()
      } catch (reason) { setError(reason instanceof Error ? reason.message : 'Collection status unavailable') }
    }, POLL_MS)
    return () => window.clearInterval(timer)
  }, [activeRun, refresh])

  async function startCollection() {
    setError(null)
    try { setActiveRun(await api.startRun()) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Collection could not start') }
  }

  const running = activeRun && ['queued', 'running'].includes(activeRun.status)
  const articles = data?.articles.filter(article => article.title.toLowerCase().includes(query.toLowerCase()) || article.source_name.toLowerCase().includes(query.toLowerCase())) ?? []

  return <div className="shell">
    <header className="topbar"><a className="brand" href="#top"><span><Radio size={20} /></span>NEWSPULSE<small>INTELLIGENCE</small></a><nav><a href="#trends">Trends</a><a href="#coverage">Coverage</a><a href="#pipeline">Pipeline</a></nav><div className="system-status"><i /> All systems operational</div></header>
    <main id="top">
      <section className="hero"><div className="eyebrow"><Sparkles size={14} /> LIVE TECHNOLOGY SIGNALS</div><div className="hero-layout"><div><h1>See the story<br/><em>behind the headlines.</em></h1><p>NewsPulse collects technology coverage, removes noise, groups related reporting, and surfaces the subjects gaining momentum across independent sources.</p><div className="hero-actions"><button className="primary" onClick={startCollection} disabled={Boolean(running)}>{running ? <LoaderCircle className="spin" size={18}/> : <Play size={18} fill="currentColor"/>}{running ? 'Pipeline running' : 'Collect latest news'}</button><button className="secondary" onClick={() => void refresh()}><RefreshCw size={17}/> Refresh dashboard</button></div></div><div className="pulse-orbit"><div className="orbit one"/><div className="orbit two"/><div className="pulse-core"><Activity size={36}/><span>LIVE</span></div><b className="node n1">INGEST</b><b className="node n2">NORMALIZE</b><b className="node n3">CLUSTER</b></div></div></section>
      {error && <div className="notice error">{error}</div>}
      {activeRun && <section className={`run-banner ${activeRun.status}`}><div><LoaderCircle className={running ? 'spin' : ''} size={20}/><div><strong>Collection {activeRun.status}</strong><span>{activeRun.status === 'completed' ? 'The dashboard now reflects the latest data.' : 'Workers are collecting and processing sources concurrently.'}</span></div></div><div className="run-stats"><span><b>{activeRun.collected}</b> collected</span><span><b>{activeRun.inserted}</b> new</span><span><b>{activeRun.duplicates}</b> duplicates</span><span><b>{activeRun.failures}</b> source failures</span></div></section>}
      <section className="metrics" aria-label="Pipeline summary"><MetricCard label="ACTIVE SOURCES" value={data?.metrics.sources ?? '—'} detail="Independent feeds" icon={Network}/><MetricCard label="ARTICLES INDEXED" value={data?.metrics.articles ?? '—'} detail="Canonical records" icon={Newspaper} tone="violet"/><MetricCard label="STORY CLUSTERS" value={data?.metrics.stories ?? '—'} detail="Related coverage" icon={Layers3} tone="amber"/><MetricCard label="PIPELINE STATE" value={data?.metrics.latest_run_status ?? '—'} detail="Redis worker queue" icon={Server}/></section>
      <section id="trends" className="section"><div className="section-heading"><div><span>INTELLIGENCE LAYER</span><h2>Trending story clusters</h2><p>Scores combine recency, source diversity, and coverage volume.</p></div><div className="legend"><i/> Trend score</div></div>
        {loading ? <div className="loading"><LoaderCircle className="spin"/> Loading intelligence…</div> : data?.stories.length ? <div className="story-grid">{data.stories.map((story, index) => <article className="story-card" key={story.id}><div className="rank">{String(index + 1).padStart(2, '0')}</div><div className="story-main"><span className="topic">{story.topic}</span><h3>{story.title}</h3><div className="story-meta"><span>{story.source_count} sources</span><span>{story.article_count} articles</span><span>{formatDistanceToNow(new Date(story.last_seen_at), { addSuffix: true })}</span></div></div><div className="score" style={{ '--score': `${story.trend_score}%` } as React.CSSProperties}><strong>{Math.round(story.trend_score)}</strong><span>TREND</span></div></article>)}</div> : <EmptyState />}
      </section>
      <section id="coverage" className="section coverage"><div className="section-heading"><div><span>SOURCE STREAM</span><h2>Latest coverage</h2><p>Article metadata only. Every headline links back to its original publisher.</p></div><label className="search"><Search size={17}/><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search headlines or sources"/></label></div><div className="article-list">{articles.map(article => <a href={article.canonical_url} target="_blank" rel="noreferrer" className="article-row" key={article.id}><div className="source-mark">{article.source_name.slice(0,2).toUpperCase()}</div><div><span>{article.source_name} · {formatDistanceToNow(new Date(article.published_at), { addSuffix: true })}</span><h3>{article.title}</h3><p>{article.excerpt ?? 'No publisher excerpt was provided.'}</p></div><ArrowUpRight size={19}/></a>)}</div></section>
      <section id="pipeline" className="pipeline-section"><div><span>ENGINEERING VIEW</span><h2>Built for reliable ingestion</h2><p>The interface is the visible layer of a fault-tolerant asynchronous pipeline. Every stage has a focused responsibility and can evolve independently.</p></div><div className="pipeline-flow">{[[Radio,'Collect','RSS / Atom'],[Database,'Normalize','Clean metadata'],[Layers3,'Cluster','Related stories'],[Activity,'Score','Live trends']].map(([Icon,title,detail], index) => { const StageIcon = Icon as typeof Radio; return <div className="stage" key={String(title)}><b>{index + 1}</b><StageIcon size={22}/><strong>{String(title)}</strong><span>{String(detail)}</span></div>})}</div></section>
    </main><footer><div className="brand compact"><span><Radio size={16}/></span>NEWSPULSE</div><p>Technology news metadata intelligence · Built with FastAPI, Redis, PostgreSQL and React</p><a href="/api/docs" target="_blank">API documentation <ArrowUpRight size={14}/></a></footer>
  </div>
}

function EmptyState() { return <div className="empty"><Database size={30}/><h3>No stories indexed yet</h3><p>Run the collection pipeline to ingest and analyze current technology coverage.</p></div> }

