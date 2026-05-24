import './globals.css'
import Link from 'next/link'
export default function RootLayout({children}:{children:React.ReactNode}) {
  const nav=[['项目','/projects'],['角色','/characters'],['场景','/scenes'],['镜头','/shots'],['提示词','/prompts'],['任务','/tasks'],['资产','/assets']]
  return <html lang='zh-CN'><body><div className='p-4 flex gap-3 flex-wrap border-b'>{nav.map(([t,u])=><Link key={u} href={u} className='px-3 py-1 rounded bg-white border'>{t}</Link>)}</div><main className='p-6'>{children}</main></body></html>
}
