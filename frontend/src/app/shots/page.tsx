'use client'

import { useEffect, useMemo, useState } from 'react'

type Shot = {
  id: number
  episode: number
  scene_no: string
  shot_no: string
  duration_sec: number
  aspect_ratio: string
  shot_size: string
  camera_angle: string
  action: string
  dialogue: string
  visual_requirements: string
  negative_prompt: string
  status: string
}

const emptyForm = {
  episode: 1,
  scene_no: '',
  shot_no: '',
  duration_sec: 5,
  aspect_ratio: '16:9',
  shot_size: '中景',
  camera_angle: '平视',
  action: '',
  dialogue: '',
  visual_requirements: '',
  negative_prompt: '',
  status: 'draft'
}

const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export default function Page() {
  const [shots, setShots] = useState<Shot[]>([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Shot | null>(null)
  const [form, setForm] = useState<any>(emptyForm)

  const title = useMemo(() => (editing ? '编辑镜头' : '新增镜头'), [editing])

  async function fetchShots() {
    const res = await fetch(`${apiBase}/api/shots`)
    setShots(await res.json())
  }

  useEffect(() => { fetchShots() }, [])

  function onCreate() { setEditing(null); setForm(emptyForm); setOpen(true) }
  function onEdit(shot: Shot) { setEditing(shot); setForm(shot); setOpen(true) }

  async function onSave() {
    const url = editing ? `${apiBase}/api/shots/${editing.id}` : `${apiBase}/api/shots`
    const method = editing ? 'PUT' : 'POST'
    await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
    setOpen(false)
    await fetchShots()
  }

  async function onDelete(id: number) {
    await fetch(`${apiBase}/api/shots/${id}`, { method: 'DELETE' })
    await fetchShots()
  }

  return <div className='space-y-4'>
    <div className='flex justify-between items-center'><h1 className='text-xl font-bold'>镜头管理</h1><button onClick={onCreate} className='px-3 py-2 rounded bg-slate-900 text-white'>新增镜头</button></div>
    <div className='bg-white border rounded-xl overflow-auto'>
      <table className='w-full text-sm'>
        <thead className='bg-slate-100'><tr>{['集数','场次','镜头号','时长','画幅','景别','机位','状态','操作'].map(h=><th key={h} className='p-2 text-left'>{h}</th>)}</tr></thead>
        <tbody>{shots.map(s=><tr key={s.id} className='border-t'><td className='p-2'>{s.episode}</td><td className='p-2'>{s.scene_no}</td><td className='p-2'>{s.shot_no}</td><td className='p-2'>{s.duration_sec}s</td><td className='p-2'>{s.aspect_ratio}</td><td className='p-2'>{s.shot_size}</td><td className='p-2'>{s.camera_angle}</td><td className='p-2'>{s.status}</td><td className='p-2 space-x-2'><button onClick={()=>onEdit(s)} className='underline'>编辑</button><button onClick={()=>onDelete(s.id)} className='underline text-red-600'>删除</button></td></tr>)}</tbody>
      </table>
    </div>

    {open && <div className='fixed inset-0 bg-black/30 flex justify-end'>
      <div className='w-full max-w-xl bg-white h-full p-4 overflow-y-auto'>
        <div className='flex justify-between items-center mb-4'><h2 className='font-semibold'>{title}</h2><button onClick={()=>setOpen(false)}>关闭</button></div>
        <div className='grid grid-cols-2 gap-3'>
          {['episode','scene_no','shot_no','duration_sec','aspect_ratio','shot_size','camera_angle','status'].map((k)=><input key={k} value={form[k]} onChange={(e)=>setForm({...form,[k]: k==='episode'||k==='duration_sec'?Number(e.target.value):e.target.value})} placeholder={k} className='border rounded p-2' />)}
          <textarea value={form.action} onChange={e=>setForm({...form,action:e.target.value})} placeholder='动作' className='border rounded p-2 col-span-2' />
          <textarea value={form.dialogue} onChange={e=>setForm({...form,dialogue:e.target.value})} placeholder='台词' className='border rounded p-2 col-span-2' />
          <textarea value={form.visual_requirements} onChange={e=>setForm({...form,visual_requirements:e.target.value})} placeholder='视觉要求' className='border rounded p-2 col-span-2' />
          <textarea value={form.negative_prompt} onChange={e=>setForm({...form,negative_prompt:e.target.value})} placeholder='负面提示词' className='border rounded p-2 col-span-2' />
        </div>
        <button onClick={onSave} className='mt-4 px-3 py-2 rounded bg-slate-900 text-white'>保存</button>
      </div>
    </div>}
  </div>
}
