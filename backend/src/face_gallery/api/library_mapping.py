from face_gallery.models.photo import LibraryOut


def row_to_library(row) -> LibraryOut:
    return LibraryOut(
        id=row[0],
        root_path=row[1],
        last_scan_at=row[2],
        photo_count=int(row[3] or 0),
        person_count=int(row[4] or 0),
        cover_person_id=row[5],
    )
