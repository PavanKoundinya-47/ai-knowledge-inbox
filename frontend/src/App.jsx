import {useCallback,useEffect,useMemo,useState} from 'react'
import {BrainCircuit,Plus,Search,Link2,FileText,Sparkles,BookOpen,CheckCircle2,Clock3,AlertCircle,LoaderCircle,Send,ExternalLink,RefreshCw,Zap,ArrowUpRight} from 'lucide-react'
import {getItems,ingest,askQuestion} from './services/api'

const examples=['What are the key ideas in my notes?','Summarize the content I saved recently','What do my sources say about async workflows?']
const dateLabel=v=>v?new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric'}).format(new Date(v)):'Just now'

export default function App(){
 const [items,setItems]=useState([]),[kind,setKind]=useState('note'),[content,setContent]=useState(''),[url,setUrl]=useState('')
 const [question,setQuestion]=useState(''),[answer,setAnswer]=useState(null),[busy,setBusy]=useState(false),[asking,setAsking]=useState(false)
 const [error,setError]=useState(''),[toast,setToast]=useState(''),[filter,setFilter]=useState('all')
 const refresh=useCallback(async()=>{try{setItems((await getItems()).items||[]);setError('')}catch(e){setError(e.message)}},[])
 useEffect(()=>{refresh();const id=setInterval(refresh,4000);return()=>clearInterval(id)},[refresh])
 const ready=items.filter(i=>i.status==='ready').length,processing=items.filter(i=>i.status==='processing').length
 const filtered=useMemo(()=>items.filter(i=>filter==='all'||i.source_type===filter),[items,filter])
 async function save(e){e.preventDefault();setError('');const payload=kind==='note'?{type:'note',content:content.trim()}:{type:'url',url:url.trim()}
  if(kind==='note'&&!payload.content)return setError('Write a note before adding it.')
  if(kind==='url'&&!payload.url)return setError('Enter a URL to save.')
  setBusy(true);try{await ingest(payload);setContent('');setUrl('');setToast('Added to your knowledge inbox');setTimeout(()=>setToast(''),2800);await refresh()}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function ask(value=question){if(!value.trim())return;setQuestion(value);setAsking(true);setError('');setAnswer(null);try{setAnswer(await askQuestion(value.trim()))}catch(e){setError(e.message)}finally{setAsking(false)}}
 return <div className="shell">
  <aside className="sidebar"><div className="brand"><div className="brand-icon"><BrainCircuit/></div><div><b>inbox<span>.</span></b><small>BY TURIUM</small></div></div>
   <label className="nav-label">WORKSPACE</label><button className="nav active"><BookOpen size={17}/>Knowledge inbox <em>{items.length}</em></button><button className="nav" onClick={()=>document.getElementById('ask')?.scrollIntoView({behavior:'smooth'})}><Sparkles size={17}/>Ask AI</button>
   <div className="side-line"/><label className="nav-label library-label">YOUR LIBRARY</label>
   <button className={`nav secondary ${filter==='all'?'chosen':''}`} onClick={()=>setFilter('all')}><BookOpen size={16}/>All sources</button><button className={`nav secondary ${filter==='note'?'chosen':''}`} onClick={()=>setFilter('note')}><FileText size={16}/>Notes</button><button className={`nav secondary ${filter==='url'?'chosen':''}`} onClick={()=>setFilter('url')}><Link2 size={16}/>Web pages</button>
   <div className="sidebar-bottom"><div className="mini-card"><Zap size={17}/><div><b>Your second brain</b><small>Your ideas, connected.</small></div></div><div className="profile"><div className="avatar">K</div><div><b>Knowledge space</b><small>Personal workspace</small></div><i/></div></div>
  </aside>
  <main><header className="topbar"><div><span>Workspace</span><b>/</b><strong>Knowledge inbox</strong></div><div className="local"><i/> Local workspace <span className="avatar small-avatar">K</span></div></header>
   <div className="content"><section className="hero"><div><div className="eyebrow"><i/> YOUR PERSONAL KNOWLEDGE HUB</div><h1>Your knowledge,<br/><span>at your fingertips.</span></h1><p>Save what matters. Ask better questions. Connect the dots.</p></div><div className="hero-art"><div className="ring r1"/><div className="ring r2"/><div className="brain"><BrainCircuit size={34}/></div><div className="float f1"><FileText size={15}/></div><div className="float f2"><Link2 size={15}/></div><div className="float f3"><Sparkles size={15}/></div></div></section>
   <section className="stats"><div className="stat"><div className="stat-icon purple"><BookOpen/></div><div><label>Total sources</label><b>{items.length}</b><small>Across your knowledge base</small></div></div><div className="stat"><div className="stat-icon green"><CheckCircle2/></div><div><label>Indexed & ready</label><b>{ready}</b><small>Available for AI search</small></div></div><div className="stat"><div className="stat-icon amber"><Clock3/></div><div><label>Processing</label><b>{processing}</b><small>Being prepared for search</small></div></div></section>
   {error&&<div className="alert"><AlertCircle size={17}/>{error}<button onClick={()=>setError('')}>×</button></div>}{toast&&<div className="toast"><CheckCircle2 size={16}/>{toast}</div>}
   <section className="two-col"><article className="panel"><div className="panel-head"><div><label className="kicker">GROW YOUR LIBRARY</label><h2>Add to your knowledge</h2><p>Capture an idea or bring in a useful web page.</p></div><div className="panel-icon"><Plus/></div></div>
    <div className="tabs"><button className={kind==='note'?'tab selected':'tab'} onClick={()=>setKind('note')}><FileText size={15}/>Text note</button><button className={kind==='url'?'tab selected':'tab'} onClick={()=>setKind('url')}><Link2 size={15}/>Web URL</button></div>
    <form onSubmit={save}><label className="field">{kind==='note'?'YOUR NOTE':'PAGE URL'}{kind==='note'?<textarea value={content} onChange={e=>setContent(e.target.value)} placeholder="A thought, a meeting takeaway, a useful snippet..." rows="5" maxLength="100000"/>:<div className="input-wrap"><Link2 size={17}/><input type="url" value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://example.com/article"/></div>}{kind==='url'&&<small>Readable page content will be extracted and indexed.</small>}</label>
    <div className="form-foot"><span>✦ Private to this workspace</span><button className="primary" disabled={busy}>{busy?<LoaderCircle className="spin" size={15}/>:<Plus size={15}/>} {busy?'Adding...':'Add to inbox'}</button></div></form>
   </article>
   <article className="panel" id="ask"><div className="panel-head"><div><label className="kicker">RETRIEVAL-AUGMENTED GENERATION</label><h2>Ask your knowledge</h2><p>Answers grounded in what you've saved.</p></div><div className="panel-icon"><Sparkles/></div></div>
    <form className="ask-form" onSubmit={e=>{e.preventDefault();ask()}}><label className="field">YOUR QUESTION<div className="input-wrap"><Search size={17}/><input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask anything in your library..."/></div></label><button className="ask-button" disabled={asking||!question.trim()}>{asking?<LoaderCircle className="spin" size={15}/>:<Send size={15}/>} {asking?'Thinking...':'Ask AI'}<span>↵</span></button></form>
    {!answer&&!asking&&<div className="suggestions"><label>TRY ASKING</label>{examples.map(q=><button key={q} onClick={()=>ask(q)}>{q}<ArrowUpRight size={14}/></button>)}</div>}
    {asking&&<div className="loading-answer"><Sparkles size={20}/><div><b>Connecting the dots...</b><small>Searching saved knowledge and preparing an answer.</small></div></div>}
    {answer&&<div className="answer"><div className="answer-label"><Sparkles size={14}/> AI RESPONSE <button onClick={()=>setAnswer(null)}>Clear</button></div><p>{answer.answer}</p><label className="kicker">SOURCES · {answer.sources.length}</label>{answer.sources.map(s=><div className="source" key={s.chunk_id}><div className="source-icon">{s.source_type==='url'?<Link2 size={14}/>:<FileText size={14}/>}</div><div><b>{s.title}</b><p>{s.snippet}</p><small>Relevance {Math.round(s.score*100)}%</small></div>{s.source_url&&<a href={s.source_url} target="_blank" rel="noreferrer"><ExternalLink size={14}/></a>}</div>)}</div>}
    <div className="note-foot"><Sparkles size={12}/> AI answers are generated from your saved sources. Verify important details.</div>
   </article></section>
   <section className="panel collection"><div className="collection-head"><div><label className="kicker">YOUR COLLECTION</label><h2>Recently saved <span>{filtered.length}</span></h2></div><button className="refresh" onClick={refresh}><RefreshCw size={14}/> Refresh</button></div>
    {filtered.length===0?<div className="empty"><div><BookOpen size={22}/></div><b>Your knowledge space starts here</b><p>Save a note or web page above. Your sources will show up here.</p></div>:<div className="items"><div className="table-head"><span>SOURCE</span><span>TYPE</span><span>STATUS</span><span>ADDED</span><span/></div>{filtered.map(i=><div className="item-row" key={i.id}><div className="item-name"><div className={i.source_type==='url'?'item-icon url':'item-icon note'}>{i.source_type==='url'?<Link2 size={16}/>:<FileText size={16}/>}</div><div><b>{i.title}</b>{i.source_url&&<small>{i.source_url}</small>}{i.status==='failed'&&<small className="failed-text">{i.error_message}</small>}</div></div><span className="type">{i.source_type==='url'?'Web page':'Text note'}</span><span className={`status ${i.status}`}>{i.status==='ready'?<CheckCircle2 size={13}/>:i.status==='failed'?<AlertCircle size={13}/>:<LoaderCircle className="spin" size={13}/>} {i.status}</span><span className="date">{dateLabel(i.created_at)}</span><span>{i.source_url&&<a className="open-link" href={i.source_url} target="_blank" rel="noreferrer"><ExternalLink size={14}/></a>}</span></div>)}</div>}
    <div className="collection-foot"><span><i/> Your knowledge is stored in your workspace database.</span><span>Powered by semantic search <Sparkles size={12}/></span></div>
   </section><footer><span>Made for curious minds.</span><b>KNOWLEDGE INBOX · TURIUM</b></footer></div>
  </main>
 </div>
}
