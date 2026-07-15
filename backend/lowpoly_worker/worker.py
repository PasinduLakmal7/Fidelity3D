import os
import time
from celery import Celery
from shared.database import SessionLocal
from shared.models import Job, JobStatus

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("lowpoly_worker", broker=REDIS_URL)

@celery_app.task(name="process_free_job")
def process_free_job(job_id: str):
    """
    Listens to 'free_queue'. Simulates TripoSR 3D generation.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return
        
        # 1. Update status
        job.status = JobStatus.FREE_PROCESSING
        db.commit()
        
        # 2. Simulate TripoSR model generation
        from lowpoly_worker.triposr_engine import generate_3d_mesh
        generate_3d_mesh(job.image_paths, f"outputs/{job_id}/lowpoly.obj")
        
        # 3. Update DB (temporarily)
        job.status = JobStatus.FREE_COMPLETED
        db.commit()
        
        # 4. Send to Animation Worker (is_premium=False)
        celery_app.send_task("process_animation_job", args=[job_id, False], queue="animation_queue")
        
    finally:
        db.close()
