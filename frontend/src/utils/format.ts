export function libraryDisplayName(rootPath: string): string {
  const normalized = rootPath.replace(/\\/g, '/')
  const parts = normalized.split('/').filter(Boolean)
  return parts[parts.length - 1] ?? rootPath
}

export function formatLastScan(iso: string | null): string {
  if (!iso) return 'Not scanned yet'
  const d = new Date(iso.includes('T') ? iso : `${iso.replace(' ', 'T')}Z`)
  if (Number.isNaN(d.getTime())) return iso
  const now = new Date()
  const sameDay =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()
  const time = d.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
  if (sameDay) return `Today, ${time}`
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function formatDurationMs(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)}s`
  const totalSec = Math.floor(ms / 1000)
  const h = Math.floor(totalSec / 3600)
  const m = Math.floor((totalSec % 3600) / 60)
  const s = totalSec % 60
  if (h > 0) return `${h}h ${m}m ${s}s`
  if (m > 0) return `${m}m ${s.toString().padStart(2, '0')}s`
  return `${s}s`
}

export function jobElapsedMs(job: {
  created_at: string | null
  updated_at: string | null
  status: string
}): number {
  if (!job.created_at) return 0
  const start = parseSqliteDate(job.created_at)
  const end =
    job.status === 'done' || job.status === 'failed'
      ? parseSqliteDate(job.updated_at ?? job.created_at)
      : Date.now()
  return Math.max(0, end - start)
}

function parseSqliteDate(iso: string): number {
  const normalized = iso.includes('T') ? iso : iso.replace(' ', 'T')
  const d = new Date(normalized.endsWith('Z') ? normalized : `${normalized}Z`)
  return d.getTime()
}

export function parseCurrentFile(message: string | null): string | null {
  if (!message) return null
  const m = message.match(/^(?:Indexed|Skipped|Error)\s+(.+?)(?:\s+\(|$)/)
  return m?.[1] ?? null
}

export function parseJobSummary(message: string | null): string {
  if (!message) return '—'
  if (message.startsWith('Complete.')) return message
  return message
}
