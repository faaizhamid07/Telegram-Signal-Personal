import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Bell, Search, Plus, Trash2, RadioTower, KeyRound, ExternalLink, RefreshCw, LogOut, ShieldCheck, Send } from 'lucide-react'
import './style.css'

function App() {
  const [token, setToken] = useState(
    () => sessionStorage.getItem('dashboard_token') || ''
    )
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [tab, setTab] = useState('matches')
  const [groups, setGroups] = useState([])
  const [keywords, setKeywords] = useState([])
  const [matches, setMatches] = useState([])
  const [groupPeer, setGroupPeer] = useState('')
  const [groupTitle, setGroupTitle] = useState('')
  const [term, setTerm] = useState('')
  const [busy, setBusy] = useState(false)

  async function api(path, options = {}) {
    const res = await fetch(path, { ...options, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) } })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || `Request failed (${res.status})`)
    }
    if (res.status === 204) return null
    return res.json()
  }
  async function refresh() {
    if (!token) return
    setBusy(true); setError('')
    try {
      const [g, k, m] = await Promise.all([api('/api/groups'), api('/api/keywords'), api('/api/matches')])
      setGroups(g); setKeywords(k); setMatches(m)
    } catch (e) { setError(e.message); if (e.message.includes('log in')) setToken('') }
    finally { setBusy(false) }
  }
  async function doLogin(e) {
    e.preventDefault(); setError('')
    try { const r = await api('/api/login', { method: 'POST', body: JSON.stringify({ password }) }); setToken(r.token) }
    catch (e) { setError(e.message) }
  }
  useEffect(() => {
    if (!token) {
      sessionStorage.removeItem('dashboard_token')
      return
    }

    sessionStorage.setItem('dashboard_token', token)
    refresh()
    const interval = window.setInterval(() => {
      refresh()
    }, 5000)
    
    return () => window.clearInterval(interval)
  }, [token])
  
  async function action(fn) { try { setError(''); await fn(); await refresh() } catch (e) { setError(e.message) } }
  async function addGroup(e) { e.preventDefault(); await action(async () => { await api('/api/groups', { method: 'POST', body: JSON.stringify({ peer: groupPeer, title: groupTitle || groupPeer }) }); setGroupPeer(''); setGroupTitle('') }) }
  async function addKeyword(e) { e.preventDefault(); await action(async () => { await api('/api/keywords', { method: 'POST', body: JSON.stringify({ term }) }); setTerm('') }) }

  if (!token) return <main className="login-shell"><div className="login-card"><div className="brand-mark"><RadioTower size={25}/></div><p className="eyebrow">PERSONAL TELEGRAM MONITOR</p><h1>Telegram Signal</h1><p className="muted">Catch the messages that matter. Leave the scrolling behind.</p><form onSubmit={doLogin}><label>Dashboard password</label><input autoFocus type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter your password" required/><button className="primary full"><KeyRound size={17}/> Unlock dashboard</button></form>{error && <p className="error">{error}</p>}<div className="safe-note"><ShieldCheck size={16}/> Private dashboard · Personal account monitoring</div></div></main>

  return <div className="app-shell">
    <aside className="sidebar"><div className="brand"><div className="brand-mark"><RadioTower size={22}/></div><div><strong>Telegram Signal</strong><small>PERSONAL WORKSPACE</small></div></div>
      <div className="nav-label">WORKSPACE</div>
      {[['matches', Bell, 'Matched messages'], ['groups', RadioTower, 'Monitored groups'], ['keywords', Search, 'Keywords']].map(([id, Icon, label]) => <button key={id} onClick={() => setTab(id)} className={`nav-item ${tab===id?'active':''}`}><Icon size={18}/>{label}{id==='matches' && <span className="nav-count">{matches.length}</span>}</button>)}
      <div className="sidebar-bottom"><div className="status"><span className="status-dot"/> Dashboard online</div><a className="nav-item" href="https://t.me/whatashot07" target="_blank" rel="noreferrer" title="Message me on Telegram"><Send size={17}/> Contact me</a><button className="nav-item" onClick={() => { setToken(''); setPassword('') }}><LogOut size={17}/> Lock dashboard</button></div>
    </aside>
    <main className="content"><header><div><p className="eyebrow">YOUR TELEGRAM, FILTERED</p><h1>{tab==='matches'?'Matched messages':tab==='groups'?'Monitored groups':'Keyword rules'}</h1><p className="muted">{tab==='matches'?'Only the messages that match your signal.':tab==='groups'?'Choose the groups worth watching.':'Tell Telegram Signal what to look for.'}</p></div><div className="header-actions">{tab==='matches' && <button className="icon-button danger" title="Clear all matches" onClick={() => action(async () => { await api('/api/matches', { method: 'DELETE' }) })}><Trash2 size={17}/></button>}<button className="icon-button" title="Refresh" onClick={refresh}><RefreshCw size={17} className={busy?'spin':''}/></button></div></header>
      {error && <div className="error-banner">{error}</div>}
      <div className="stats"><div className="stat-card"><span>Saved matches</span><strong>{matches.length}</strong><small>Latest 100 records</small></div><div className="stat-card"><span>Monitored groups</span><strong>{groups.filter(x=>x.enabled).length}</strong><small>{groups.length} configured</small></div><div className="stat-card"><span>Active keywords</span><strong>{keywords.filter(x=>x.enabled).length}</strong><small>{keywords.length} configured</small></div></div>
      {tab==='matches' && <section className="panel"><div className="panel-head"><div><h2>Recent matches</h2><p className="muted">New messages matching enabled keywords.</p></div><span className="pill">{matches.length} shown</span></div>{matches.length===0?<div className="empty"><div className="empty-icon"><Bell size={22}/></div><h3>No matches yet</h3><p>Add a group and a keyword, then wait for a matching new message.</p></div>:<div className="match-list">{matches.map(m=><article className="match" key={m.id}><div className="match-top"><strong>{m.group_title}</strong><span>{m.created_at}</span></div><div className="tags">{m.matched_terms.split(', ').map(t=><span key={t} className="tag">{t}</span>)}</div><p className="message-text">{m.text}</p>{m.link?<a className="open-link" href={m.link} target="_blank" rel="noreferrer">Open in Telegram <ExternalLink size={14}/></a>:<span className="muted tiny">Original message link unavailable for this group</span>}</article>)}</div>}</section>}
      {tab==='groups' && <section className="panel"><div className="panel-head"><div><h2>Group sources</h2><p className="muted">Use a username (without @) or numeric Telegram peer ID.</p></div></div><form className="add-form" onSubmit={addGroup}><input value={groupPeer} onChange={e=>setGroupPeer(e.target.value)} placeholder="Group username or peer ID" required/><input value={groupTitle} onChange={e=>setGroupTitle(e.target.value)} placeholder="Display name (optional)"/><button className="primary"><Plus size={16}/> Add group</button></form><div className="row-list">{groups.map(g=><div className="config-row" key={g.id}><div className="row-icon"><RadioTower size={18}/></div><div className="row-main"><strong>{g.title}</strong><small>{g.peer}</small></div><span className={`pill ${g.enabled?'green':''}`}>{g.enabled?'Enabled':'Paused'}</span><button className="text-button" onClick={()=>action(()=>api(`/api/groups/${g.id}`,{method:'PATCH'}))}>{g.enabled?'Pause':'Enable'}</button><button className="danger-button" title="Remove group" onClick={()=>action(()=>api(`/api/groups/${g.id}`,{method:'DELETE'}))}><Trash2 size={16}/></button></div>)}</div></section>}
      {tab==='keywords' && <section className="panel"><div className="panel-head"><div><h2>Keyword rules</h2><p className="muted">Case-insensitive literal words and phrases. Any enabled keyword triggers an alert.</p></div></div><form className="add-form keyword-form" onSubmit={addKeyword}><input value={term} onChange={e=>setTerm(e.target.value)} placeholder="e.g. internship, GATE 2027, hiring" required/><button className="primary"><Plus size={16}/> Add keyword</button></form><div className="row-list">{keywords.map(k=><div className="config-row" key={k.id}><div className="row-icon"><Search size={18}/></div><div className="row-main"><strong>{k.term}</strong><small>Literal phrase match · case-insensitive</small></div><span className={`pill ${k.enabled?'green':''}`}>{k.enabled?'Active':'Paused'}</span><button className="text-button" onClick={()=>action(()=>api(`/api/keywords/${k.id}`,{method:'PATCH'}))}>{k.enabled?'Pause':'Enable'}</button><button className="danger-button" title="Remove keyword" onClick={()=>action(()=>api(`/api/keywords/${k.id}`,{method:'DELETE'}))}><Trash2 size={16}/></button></div>)}</div></section>}
      <footer>Telegram Signal <span>·</span> Personal keyword monitoring <span>·</span> <a href="/docs" target="_blank" rel="noreferrer">API docs</a></footer>
    </main>
  </div>
}
createRoot(document.getElementById('root')).render(<App/>)
