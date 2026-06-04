from face_gallery.models.job import JobOut


def row_to_job(row, *, queue_position: int | None = None) -> JobOut:
    return JobOut(
        id=row[0],
        library_id=row[1],
        type=row[2],
        status=row[3],
        progress=float(row[4]),
        message=row[5],
        force=bool(row[6]),
        created_at=row[7],
        updated_at=row[8],
        library_root_path=row[9],
        queue_position=queue_position,
    )


def attach_queue_positions(jobs: list[JobOut]) -> list[JobOut]:
    for i, job in enumerate(jobs):
        job.queue_position = i + 1
    return jobs
