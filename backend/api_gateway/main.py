import uuid
from typing import List
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from shared.database import engine, Base, get_db
from shared.models import Job, JobStatus
from shared.local_storage import save_uploaded_images
from api_gateway.core.celery_config import celery_app

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fidelity3D API Gateway")

@app.post("/upload")
async def upload_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Accepts 4 image files, creates a DB record, and triggers the FREE pipeline.
    """
    if len(files) != 4:
        raise HTTPException(status_code=400, detail="Exactly 4 images are required.")
    
    job_id = str(uuid.uuid4())
    
    try:
        # 1. Save images to backend/uploads/
        image_paths_str = await save_uploaded_images(files, job_id)
        
        # 2. Create Job record in SQLite
        new_job = Job(
            job_id=job_id,
            status=JobStatus.FREE_PENDING,
            image_paths=image_paths_str
        )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        # 3. Send task to lowpoly_worker via Celery Redis Broker
        celery_app.send_task("process_free_job", args=[job_id], queue="free_queue")
        
        return {
            "message": "Images uploaded successfully! Free tier processing started.",
            "job_id": job_id,
            "status": new_job.status.value
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Mock Stripe Webhook that triggers the PREMIUM pipeline.
    Expects payload: {"job_id": "uuid-...", "status": "paid"}
    """
    payload = await request.json()
    job_id = payload.get("job_id")
    payment_status = payload.get("status")
    
    if not job_id or payment_status != "paid":
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
        
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Update status to PAID_PROCESSING
    job.status = JobStatus.PAID_PROCESSING
    db.commit()
    
    # Send task to premium_worker
    celery_app.send_task("process_premium_job", args=[job_id], queue="premium_queue")
    
    return {"message": "Payment successful! Premium processing started."}


@app.get("/status/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    """
    Returns the current status of a job.
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "output_file_path": job.output_file_path
    }
