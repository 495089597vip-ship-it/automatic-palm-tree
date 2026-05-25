'use client'

import { useEffect, useState } from 'react'
import { SimpleCard } from '@/components/simple-card'

type Project = {
  id: number
  name: string
  description: string
}

const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export default function Page() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string>('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  async function loadProjects() {
    try {
      setError('')
      setLoading(true)
      const res = await fetch(`${apiBase}/api/projects`, { cache: 'no-store' })
      if (!res.ok) throw new Error(`加载项目失败: ${res.status}`)
      const data = await res.json()
      setProjects(Array.isArray(data) ? data : [])
    } catch (e) {
      setError(e instanceof Error ? e.message : '加载项目失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProjects()
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) {
      setError('项目名称不能为空')
      return
    }

    try {
      setError('')
      setSubmitting(true)
      const res = await fetch(`${apiBase}/api/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), description: description.trim() })
      })
      if (!res.ok) throw new Error(`创建项目失败: ${res.status}`)

      setName('')
      setDescription('')
      await loadProjects()
    } catch (e) {
      setError(e instanceof Error ? e.message : '创建项目失败')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className='space-y-4'>
      <SimpleCard title='新建项目'>
        <form onSubmit={onSubmit} className='space-y-3'>
          <div>
            <label className='block text-sm mb-1'>名称</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className='w-full border rounded p-2'
              placeholder='请输入项目名称'
            />
          </div>
          <div>
            <label className='block text-sm mb-1'>描述</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className='w-full border rounded p-2'
              placeholder='请输入项目描述'
              rows={3}
            />
          </div>
          <button
            type='submit'
            disabled={submitting}
            className='px-3 py-2 rounded bg-slate-900 text-white disabled:opacity-50'
          >
            {submitting ? '创建中...' : '新建项目'}
          </button>
        </form>
      </SimpleCard>

      <SimpleCard title='项目列表'>
        {loading ? (
          <p>加载中...</p>
        ) : error ? (
          <p className='text-red-600'>{error}</p>
        ) : projects.length === 0 ? (
          <p>暂无项目，请创建第一个项目</p>
        ) : (
          <div className='overflow-auto'>
            <table className='w-full text-sm'>
              <thead className='bg-slate-100'>
                <tr>
                  <th className='p-2 text-left'>ID</th>
                  <th className='p-2 text-left'>Name</th>
                  <th className='p-2 text-left'>Description</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.id} className='border-t'>
                    <td className='p-2'>{p.id}</td>
                    <td className='p-2'>{p.name}</td>
                    <td className='p-2'>{p.description || '-'}</td>
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
