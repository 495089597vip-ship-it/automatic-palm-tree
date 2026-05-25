'use client'

import { useEffect, useState } from 'react'
import { SimpleCard } from '@/components/simple-card'

type Character = {
  id: number
  name: string
  description: string
  appearance: string
  personality: string
  reference_image_url: string
}

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export default function Page() {
  const [items, setItems] = useState<Character[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [appearance, setAppearance] = useState('')
  const [personality, setPersonality] = useState('')
  const [referenceImageUrl, setReferenceImageUrl] = useState('')

  async function loadCharacters() {
    try {
      setError('')
      setLoading(true)
      const res = await fetch(`${apiBase}/api/characters`, { cache: 'no-store' })
      if (!res.ok) throw new Error(`加载角色失败: ${res.status}`)
      const data = await res.json()
      setItems(Array.isArray(data) ? data : [])
    } catch (e) {
      setError(e instanceof Error ? e.message : '加载角色失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCharacters()
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) {
      setError('角色名称不能为空')
      return
    }
    try {
      setError('')
      setSubmitting(true)
      const res = await fetch(`${apiBase}/api/characters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim(),
          appearance: appearance.trim(),
          personality: personality.trim(),
          reference_image_url: referenceImageUrl.trim()
        })
      })
      if (!res.ok) throw new Error(`创建角色失败: ${res.status}`)

      setName('')
      setDescription('')
      setAppearance('')
      setPersonality('')
      setReferenceImageUrl('')
      await loadCharacters()
    } catch (e) {
      setError(e instanceof Error ? e.message : '创建角色失败')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className='space-y-4'>
      <h1 className='text-xl font-bold'>Characters 角色管理</h1>

      <SimpleCard title='新建角色'>
        <form onSubmit={onSubmit} className='space-y-3'>
          <input value={name} onChange={(e) => setName(e.target.value)} className='w-full border rounded p-2' placeholder='角色名称 name' />
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} className='w-full border rounded p-2' placeholder='角色描述 description' rows={2} />
          <textarea value={appearance} onChange={(e) => setAppearance(e.target.value)} className='w-full border rounded p-2' placeholder='外貌设定 appearance' rows={2} />
          <textarea value={personality} onChange={(e) => setPersonality(e.target.value)} className='w-full border rounded p-2' placeholder='性格设定 personality' rows={2} />
          <input value={referenceImageUrl} onChange={(e) => setReferenceImageUrl(e.target.value)} className='w-full border rounded p-2' placeholder='参考图 URL reference_image_url' />
          <button type='submit' disabled={submitting} className='px-3 py-2 rounded bg-slate-900 text-white disabled:opacity-50'>
            {submitting ? '创建中...' : '新建角色'}
          </button>
        </form>
      </SimpleCard>

      <SimpleCard title='角色列表'>
        {loading ? (
          <p>加载中...</p>
        ) : error ? (
          <p className='text-red-600'>{error}</p>
        ) : items.length === 0 ? (
          <p>暂无角色，请创建第一个角色</p>
        ) : (
          <div className='overflow-auto'>
            <table className='w-full text-sm'>
              <thead className='bg-slate-100'>
                <tr>
                  <th className='p-2 text-left'>ID</th>
                  <th className='p-2 text-left'>Name</th>
                  <th className='p-2 text-left'>Description</th>
                  <th className='p-2 text-left'>Appearance</th>
                  <th className='p-2 text-left'>Personality</th>
                  <th className='p-2 text-left'>Reference Image URL</th>
                </tr>
              </thead>
              <tbody>
                {items.map((c) => (
                  <tr key={c.id} className='border-t'>
                    <td className='p-2'>{c.id}</td>
                    <td className='p-2'>{c.name}</td>
                    <td className='p-2'>{c.description || '-'}</td>
                    <td className='p-2'>{c.appearance || '-'}</td>
                    <td className='p-2'>{c.personality || '-'}</td>
                    <td className='p-2'>{c.reference_image_url || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SimpleCard>
    </div>
  )
}
