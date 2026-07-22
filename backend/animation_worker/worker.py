import os
import time
from celery import Celery
from shared.database import SessionLocal
from shared.models import Job, JobStatus
from shared.local_storage import get_output_path

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("animation_worker", broker=REDIS_URL)

@celery_app.task(name="process_animation_job")
def process_animation_job(job_id: str, is_premium: bool):
    """
    Listens to 'animation_queue'. Simulates rig generation and saves final model.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return
            
        print(f"[AnimationWorker] Job {job_id}: Applying mock RigNet/Mixamo animation...")
        from animation_worker.rig_engine import apply_animation
        output_file = get_output_path(job_id, "final_model.glb")
        input_file = f"outputs/{job_id}/highpoly.obj" if is_premium else f"outputs/{job_id}/lowpoly.obj"
        apply_animation(input_file, output_file, is_premium)
        
        # The Rig Engine now actually downloads a real animated .glb file
            
        # Update Job details
        job.output_file_path = output_file
        if is_premium:
            job.status = JobStatus.PAID_COMPLETED
        else:
            job.status = JobStatus.FREE_COMPLETED
            
        db.commit()
        print(f"[AnimationWorker] Job {job_id}: Completely finished! Output saved to {output_file}")
        
    finally:
        db.close()
