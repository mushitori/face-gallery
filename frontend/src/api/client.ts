import type {
  Job,
  Library,
  PersonListResponse,
  PhotoListResponse,
} from './types'

const base = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:28765'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
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
