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
  createLibrary: async (root_path: string) => {
    const lib = await request<Library>('/libraries', {
      method: 'POST',
      body: JSON.stringify({ root_path }),
    })
    console.log('[FaceGallery] api.createLibrary', { root_path, lib })
    return lib
  },
  startScan: async (libraryId: number, force = false) => {
    const result = await request<{ job_id: number }>(
      `/libraries/${libraryId}/scan${force ? '?force=true' : ''}`,
      { method: 'POST' },
    )
    console.log('[FaceGallery] api.startScan', { libraryId, force, result })
    return result
  },
  getJob: async (jobId: number) => {
    const job = await request<Job>(`/jobs/${jobId}`)
    console.log('[FaceGallery] api.getJob', { jobId, job })
    return job
  },
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
