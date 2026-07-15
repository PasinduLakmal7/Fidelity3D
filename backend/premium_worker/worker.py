import os
import time
from celery import Celery
from shared.database import SessionLocal
from shared.models import Job, JobStatus

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("premium_worker", broker=REDIS_URL)

@celery_app.task(name="process_premium_job")
def process_premium_job(job_id: str):
    """
    Listens to 'premium_queue'. Simulates Headless Blender task.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return
            
        print(f"[PremiumWorker] Job {job_id}: Simulating Headless Blender Retopo & PBR Bake...")
        from premium_worker.blender_scripts.run_blender import run_headless_blender
        run_headless_blender(f"outputs/{job_id}/lowpoly.obj", f"outputs/{job_id}/highpoly.obj")
        
        # Send to Animation Worker (is_premium=True)
        celery_app.send_task("process_animation_job", args=[job_id, True], queue="animation_queue")
        
    finally:
        db.close()
