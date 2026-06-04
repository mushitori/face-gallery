"""Shared SQL fragments for API routes."""

LIBRARY_SELECT = """
SELECT l.id, l.root_path, l.last_scan_at,
  (SELECT COUNT(*) FROM photos p WHERE p.library_id = l.id),
  (SELECT COUNT(*) FROM persons per WHERE per.library_id = l.id),
  (SELECT id FROM persons per
   WHERE per.library_id = l.id AND per.representative_face_id IS NOT NULL
   ORDER BY per.face_count DESC LIMIT 1)
FROM libraries l
"""

JOB_SELECT = """
SELECT j.id, j.library_id, j.type, j.status, j.progress, j.message,
  j.force, j.created_at, j.updated_at, l.root_path
FROM jobs j
JOIN libraries l ON l.id = j.library_id
"""
