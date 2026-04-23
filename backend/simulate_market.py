import requests
import time
import random

API_URL = "http://127.0.0.1:8001/api/v1/ingest/job"

# Scenario: The "AI Boom"
# We want to force the graph to show a high demand for these skills
TRENDING_SKILLS = ["Generative AI", "LangChain", "Vector Database", "RAG", "Transformer Models"]

# Standard skills (Noise)
NORMAL_SKILLS = ["Python", "Java", "SQL", "Communication", "Git"]

def generate_fake_job():
    """Generates a random job description."""
    is_ai_job = random.random() > 0.3  # 70% chance of being an AI job (High Volatility)
    
    if is_ai_job:
        title = "AI Engineer"
        skills = random.sample(TRENDING_SKILLS, k=3) + random.sample(NORMAL_SKILLS, k=2)
    else:
        title = "Backend Developer"
        skills = random.sample(NORMAL_SKILLS, k=3)
        
    return {
        "title": title,
        "required_skills": skills
    }

def start_simulation():
    print("🚀 Starting Market Simulation (The 'AI Boom' Scenario)...")
    print("Press Ctrl+C to stop.")
    
    count = 0
    try:
        while True:
            job = generate_fake_job()
            
            # Send to API
            try:
                response = requests.post(API_URL, json=job)
                if response.status_code == 200:
                    print(f"[{count}] Ingested: {job['title']} -> Skills: {job['required_skills']}")
                else:
                    print(f"❌ Error: {response.text}")
            except Exception as e:
                print(f"❌ Connection Error: {e}")

            count += 1
            time.sleep(0.5)  # Simulate 2 jobs per second
            
    except KeyboardInterrupt:
        print("\n🛑 Simulation Stopped.")

if __name__ == "__main__":
    start_simulation()