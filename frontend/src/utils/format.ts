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
  if (ms < 1000) return `${Math.max(1, Math.round(ms / 1000))}s`
  const totalSec = Math.floor(ms / 1000)
  const h = Math.floor(totalSec / 3600)
  const m = Math.floor((totalSec % 3600) / 60)
  const s = totalSec % 60
  if (h > 0) return `${h}h ${m}m ${s.toString().padStart(2, '0')}s`
  if (m > 0) return `${m}m ${s.toString().padStart(2, '0')}s`
  return `${s}s`
}

/** SQLite/API datetimes: "YYYY-MM-DD HH:MM:SS" (no timezone). */
const NAIVE_DATETIME_RE =
  /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})$/

const MONTH_SHORT = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
]

/** Parse API datetime as wall-clock components (no browser timezone). */
export function parseNaiveDateTimeMs(iso: string): number {
  const m = iso.trim().match(NAIVE_DATETIME_RE)
  if (!m) return Number.NaN
  return Date.UTC(
    Number(m[1]),
    Number(m[2]) - 1,
    Number(m[3]),
    Number(m[4]),
    Number(m[5]),
    Number(m[6]),
  )
}

/** Milliseconds between two API datetimes (same interpretation for both). */
export function naiveDateTimeDiffMs(start: string, end: string): number {
  const a = parseNaiveDateTimeMs(start)
  const b = parseNaiveDateTimeMs(end)
  if (Number.isNaN(a) || Number.isNaN(b)) return 0
  return Math.max(0, b - a)
}

/**
 * Elapsed time for scans page: updated_at − created_at from API strings only.
 * For running jobs, updated_at is refreshed on each progress tick.
 */
export function jobElapsedMs(job: {
  created_at: string | null
  updated_at: string | null
  status: string
}): number {
  if (!job.created_at) return 0
  const end = job.updated_at ?? job.created_at
  return naiveDateTimeDiffMs(job.created_at, end)
}

/** Display API datetime without local timezone conversion (Scans page). */
export function formatApiDateTime(iso: string | null): string {
  if (!iso) return '—'
  const m = iso.trim().match(NAIVE_DATETIME_RE)
  if (!m) return iso
  const year = Number(m[1])
  const month = MONTH_SHORT[Number(m[2]) - 1] ?? m[2]
  const day = Number(m[3])
  const hour24 = Number(m[4])
  const minute = m[5]
  const h12 = hour24 % 12 || 12
  const ampm = hour24 < 12 ? 'AM' : 'PM'
  return `${day} ${month} ${year}, ${h12}:${minute} ${ampm}`
}

/** @deprecated Use formatApiDateTime on Scans page for API wall-clock times. */
export function formatScanDateTime(iso: string | null): string {
  return formatApiDateTime(iso)
}

export function libraryScanLabel(
  rootPath: string | null | undefined,
  libraryId?: number,
): string {
  if (rootPath?.trim()) {
    return libraryDisplayName(rootPath)
  }
  if (libraryId != null) return `Library #${libraryId}`
  return 'Unknown library'
}

export function parseJobStats(message: string | null): {
  persons: number | null
  faces: number | null
} {
  if (!message) return { persons: null, faces: null }
  const m = message.match(/(\d+)\s+persons?\s+from\s+(\d+)\s+faces/i)
  if (!m) return { persons: null, faces: null }
  return { persons: parseInt(m[1], 10), faces: parseInt(m[2], 10) }
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
