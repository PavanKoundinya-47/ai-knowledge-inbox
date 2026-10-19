const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
async function request(path, options={}) {
  const res = await fetch(`${BASE}${path}`, {...options, headers:{'Content-Type':'application/json', ...(options.headers||{})}})
  const data = await res.json().catch(()=>({}))
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`)
  return data
}
export const getItems = () => request('/items')
export const ingest = payload => request('/ingest',{method:'POST',body:JSON.stringify(payload)})
export const askQuestion = question => request('/query',{method:'POST',body:JSON.stringify({question})})
