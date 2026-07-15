import os
from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app targeting the Redis broker
celery_app = Celery(
    "fidelity3d_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Optional: route tasks to specific queues (can also just specify queue when calling send_task)
celery_app.conf.task_routes = {
    'process_free_job': {'queue': 'free_queue'},
    'process_premium_job': {'queue': 'premium_queue'},
    'process_animation_job': {'queue': 'animation_queue'},
}
