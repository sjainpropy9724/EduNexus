import uuid
import pandas as pd
import os
import ast
from app.services.graph_builder import graph_builder

# Config
CSV_PATH = os.path.join("data_source", "dice_jobs.csv")
BATCH_SIZE = 100
LIMIT = 22000  

def clean_skills(skills_entry):
    """
    Cleans the Dice dataset 'skills' column.
    """
    if pd.isna(skills_entry):
        return []
    
    # if it looks like a list string "['Java', 'SQL']", parse it
    try:
        if str(skills_entry).strip().startswith("[") and str(skills_entry).strip().endswith("]"):
            return ast.literal_eval(skills_entry)
    except:
        pass

    # Otherwise, split by commas
    # Example: "Java, SQL, JavaScript" -> ["Java", "SQL", "JavaScript"]
    raw_skills = [s.strip() for s in str(skills_entry).split(",")]
    
    # filtering out junk (empty strings or too long phrases)
    valid_skills = [s for s in raw_skills if s and len(s) < 30]
    return valid_skills

def ingest_dice_data():
    print(f"Loading Dice.com Dataset from: {CSV_PATH}")
    
    if not os.path.exists(CSV_PATH):
        print(f"Error: File not found at {CSV_PATH}")
        print("   Please download 'dice_com-job_us_sample.csv' from Kaggle, rename to 'dice_jobs.csv', and place in 'backend/data_source/'")
        return

    # Load CSV with Pandas
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"   Dataset loaded. Total rows: {len(df)}")
    except Exception as e:
        print(f"CSV Read Error: {e}")
        return

    print("Starting Ingestion...")
    
    batch = []
    count = 0
    
    # Iterate through the DataFrame
    for index, row in df.iterrows():
        if count >= LIMIT:
            break
            
        title = row.get("jobtitle", "Unknown Role")
        raw_skills = row.get("skills", "")
        
        # Extract Skills
        skills_list = clean_skills(raw_skills)
        
        if skills_list:
            batch.append({
                "job_id": str(uuid.uuid4()),
                "title": title,
                "skills": skills_list
            })

        # Process Batch
        if len(batch) >= BATCH_SIZE:
            graph_builder.process_job_batch(batch)
            print(f"Indexed {count} jobs...")
            batch = []
            
        count += 1

    # Final Flush
    if batch:
        graph_builder.process_job_batch(batch)

    print(f"\nSUCCESS: Ingested {count} Dice.com Tech Jobs!")

if __name__ == "__main__":
    ingest_dice_data()