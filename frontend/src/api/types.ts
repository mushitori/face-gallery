export interface Library {
  id: number
  root_path: string
  last_scan_at: string | null
  photo_count: number
  person_count: number
  cover_person_id: number | null
}

export interface Job {
  id: number
  library_id: number
  type: string
  status: string
  progress: number
  message: string | null
  force: boolean
  created_at: string | null
  updated_at: string | null
  library_root_path: string | null
  queue_position: number | null
}

export interface JobsDashboard {
  active: Job | null
  queue: Job[]
  history: Job[]
}

export interface Person {
  id: number
  library_id: number
  display_name: string | null
  face_count: number
  photo_count: number
  representative_face_id: number | null
}

export interface PersonListResponse {
  items: Person[]
  library_id: number | null
}

export interface Photo {
  id: number
  library_id: number
  path: string
  face_count: number
}

export interface PhotoListResponse {
  items: Photo[]
  total: number
  page: number
  page_size: number
}
