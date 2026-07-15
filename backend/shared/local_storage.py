import os
import shutil
from typing import List
from fastapi import UploadFile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# Ensure directories exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

async def save_uploaded_images(images: List[UploadFile], job_id: str) -> str:
    """
    Saves uploaded images to the local storage (uploads/) and returns a comma-separated string of paths.
    """
    saved_paths = []
    job_dir = os.path.join(UPLOADS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    for i, image in enumerate(images):
        filename = f"{i}_{image.filename}"
        file_path = os.path.join(job_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        saved_paths.append(file_path)
        
    return ",".join(saved_paths)

def get_output_path(job_id: str, filename: str) -> str:
    """
    Returns an absolute path for saving output files inside the outputs/ directory.
    """
    job_dir = os.path.join(OUTPUTS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    return os.path.join(job_dir, filename)
