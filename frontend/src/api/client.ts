import type {
  Job,
  JobsDashboard,
  Library,
  PersonListResponse,
  PhotoListResponse,
} from './types'

const base = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:28765'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'ApiError'
  }
}

async function parseErrorMessage(res: Response): Promise<string> {
  const text = await res.text()
  try {
    const json = JSON.parse(text) as { detail?: string | { msg?: string }[] }
    if (typeof json.detail === 'string') return json.detail
    if (Array.isArray(json.detail) && json.detail[0]?.msg) {
      return json.detail[0].msg
    }
  } catch {
    /* plain text */
  }
  return text || res.statusText
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })
  if (!res.ok) {
    const message = await parseErrorMessage(res)
    throw new ApiError(res.status, message)
  }
  if (res.status === 204) {
    return undefined as T
  }
  return res.json() as Promise<T>
}

export const api = {
  base,
  health: () => request<{ status: string }>('/health'),
  listLibraries: () => request<Library[]>('/libraries'),
  createLibrary: (root_path: string) =>
    request<Library>('/libraries', {
      method: 'POST',
      body: JSON.stringify({ root_path }),
    }),
  startScan: (libraryId: number, force = false) =>
    request<{ job_id: number }>(
      `/libraries/${libraryId}/scan${force ? '?force=true' : ''}`,
      { method: 'POST' },
    ),
  getJob: (jobId: number) => request<Job>(`/jobs/${jobId}`),
  pauseJob: (jobId: number) =>
    request<void>(`/jobs/${jobId}/pause`, { method: 'POST' }),
  cancelJob: (jobId: number) =>
    request<void>(`/jobs/${jobId}/cancel`, { method: 'POST' }),
  resumeJob: (jobId: number) =>
    request<void>(`/jobs/${jobId}/resume`, { method: 'POST' }),
  retryJob: (jobId: number) =>
    request<void>(`/jobs/${jobId}/retry`, { method: 'POST' }),
  getJobsDashboard: (historyLimit = 50) =>
    request<JobsDashboard>(`/jobs/dashboard?history_limit=${historyLimit}`),
  listJobs: (bucket: 'active' | 'queue' | 'history', limit = 50) =>
    request<Job[]>(`/jobs?bucket=${bucket}&limit=${limit}`),
  listPersons: (libraryId?: number) => {
    const q = libraryId != null ? `?library_id=${libraryId}` : ''
    return request<PersonListResponse>(`/persons${q}`)
  },
  personPhotos: (personId: number, page = 1, pageSize = 60) =>
    request<PhotoListResponse>(
      `/persons/${personId}/photos?page=${page}&page_size=${pageSize}`,
    ),
  personThumbUrl: (personId: number) => `${base}/thumbs/person/${personId}`,
  photoThumbUrl: (photoId: number) => `${base}/thumbs/photo/${photoId}`,
}
