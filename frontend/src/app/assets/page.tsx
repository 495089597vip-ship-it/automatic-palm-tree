'use client'

import { useEffect, useState } from 'react'
import { SimpleCard } from '@/components/simple-card'

type Asset = {
  id: number
  project_id?: number | null
  task_id?: number | null
  asset_type: string
  provider: string
  title: string
  description?: string
  url?: string
  local_path?: string
  thumbnail_url?: string
  prompt?: string
  negative_prompt?: string
  metadata?: string
  status: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function Page() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [taskId, setTaskId] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const [form, setForm] = useState({
    project_id: '1', task_id: '', asset_type: 'image', provider: 'manual', title: '', description: '',
    url: '', local_path: '', thumbnail_url: '', prompt: '', negative_prompt: '', metadata: '', status: 'draft'
  })

  async function fetchAssets() {
    setLoading(true); setError('')
    try {
      const res = await fetch(`${API_BASE}/api/assets`, { cache: 'no-store' })
      if (!res.ok) throw new Error(`加载失败: ${res.status}`)
      setAssets(await res.json())
    } catch (e: any) { setError(e?.message || '加载失败') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchAssets() }, [])

  async function createAsset() {
    setSubmitting(true); setError('')
    try {
      const body = {
        ...form,
        project_id: form.project_id ? Number(form.project_id) : null,
        task_id: form.task_id ? Number(form.task_id) : null,
      }
      const res = await fetch(`${API_BASE}/api/assets`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      if (!res.ok) throw new Error(`创建失败: ${res.status} ${await res.text()}`)
      await fetchAssets()
    } catch (e: any) { setError(e?.message || '创建失败') }
    finally { setSubmitting(false) }
  }

  async function createFromTask() {
    if (!taskId) return
    setSubmitting(true); setError('')
    try {
      const res = await fetch(`${API_BASE}/api/tasks/${taskId}/create-asset`, { method: 'POST' })
      if (!res.ok) throw new Error(`创建失败: ${res.status} ${await res.text()}`)
      setTaskId('')
      await fetchAssets()
    } catch (e: any) { setError(e?.message || '创建失败') }
    finally { setSubmitting(false) }
  }

  return <div className='space-y-4'>
    <SimpleCard title='Assets 资产库'>
      <div className='space-y-2'>
        <button className='px-3 py-2 rounded border bg-white' onClick={fetchAssets}>刷新资产列表</button>
        {loading && <div className='text-sm text-slate-500'>加载中...</div>}
        {error && <div className='text-sm text-red-600'>{error}</div>}
      </div>
    </SimpleCard>

    <SimpleCard title='手动创建资产'>
      <div className='grid grid-cols-1 md:grid-cols-2 gap-2'>
        {Object.keys(form).map((k) => (
          <input
            key={k}
            className='border rounded p-2'
            placeholder={k}
            value={(form as any)[k]}
            onChange={(e) => setForm({ ...form, [k]: e.target.value })}
          />
        ))}
      </div>
      <button disabled={submitting || !form.title.trim()} className='mt-3 px-3 py-2 rounded bg-slate-900 text-white disabled:opacity-50' onClick={createAsset}>创建资产</button>
    </SimpleCard>

    <SimpleCard title='从任务创建资产'>
      <div className='flex gap-2'>
        <input className='border rounded p-2' placeholder='task_id' value={taskId} onChange={(e) => setTaskId(e.target.value)} />
        <button disabled={submitting || !taskId.trim()} className='px-3 py-2 rounded bg-slate-900 text-white disabled:opacity-50' onClick={createFromTask}>创建</button>
      </div>
    </SimpleCard>

    <SimpleCard title='资产列表'>
      {!loading && assets.length === 0 && <div className='text-slate-500'>暂无资产数据</div>}
      <div className='space-y-3'>
        {assets.map((a) => {
          const preview = a.thumbnail_url || a.url
          return <div key={a.id} className='border rounded p-3 space-y-1'>
            <div className='font-semibold'>#{a.id} {a.title || '(无标题)'}</div>
            <div className='text-sm'>type={a.asset_type} / provider={a.provider} / status={a.status} / task_id={a.task_id ?? '-'}</div>
            <div className='text-sm'>prompt: {a.prompt || '-'}</div>
            <div className='text-sm'>url/local_path: {a.url || '-'} {a.local_path ? `| ${a.local_path}` : ''}</div>
            <div className='text-sm break-all'>metadata: {a.metadata || '-'}</div>
            {a.asset_type === 'image' && preview && <img src={preview} alt={a.title || `asset-${a.id}`} className='max-h-48 rounded border' />}
          </div>
        })}
      </div>
    </SimpleCard>
  </div>
}
