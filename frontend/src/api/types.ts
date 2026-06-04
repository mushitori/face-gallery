export interface Library {
  id: number
  root_path: string
  last_scan_at: string | null
}

export interface Job {
  id: number
  library_id: number
  type: string
  status: string
  progress: number
  message: string | null
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
