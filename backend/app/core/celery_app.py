from celery import Celery
import os
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

# 1. Initialize Celery
# We call it "worker" and connect it to Redis
celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

# 2. Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# 3. Auto-discover tasks in our app
# (We will create the 'tasks' file in the next step)
celery_app.conf.imports = ("app.services.tasks",)

# 4. Define the Schedule (The Heartbeat)
celery_app.conf.beat_schedule = {
    "monitor-market-every-10-seconds": {
        "task": "analyze_trends",  # The name we gave the task in tasks.py
        "schedule": 10.0,          # Run every 10 seconds
    },
}
