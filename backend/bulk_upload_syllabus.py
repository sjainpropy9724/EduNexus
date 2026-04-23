import os
import asyncio
import time
import re
from app.services.ingestion import ingestion_service
from app.services.llm_parser import llm_service
from app.services.graph_builder import graph_builder
from langchain_google_genai import ChatGoogleGenerativeAI # type: ignore
from langchain.prompts import PromptTemplate # type: ignore
from langchain.output_parsers import PydanticOutputParser # type: ignore
from app.services.llm_parser import SyllabusGraph

# --- CONFIGURATION ---
PDF_DIR = os.path.join("data_source", "syllabus_pdfs")
LOG_FILE = "processed_files.txt"

# --- PASTE YOUR 4 FRESH KEYS HERE ---
# (Ensure these are valid keys from different Google Projects)
API_KEYS = [
    "AIza...............................", 
    "AIza............................",
    "AIzaS...............................",
    "AIzaS.............................."
]

class SmartIngestor:
    def __init__(self, keys):
        self.keys = keys
        self.current_key_index = 0
        self.current_model = "gemini-2.5-flash"  
        
    def get_llm(self):
        """Creates a FRESH connection with the current key."""
        api_key = self.keys[self.current_key_index]
        print(f"   🔑 Using Key #{self.current_key_index + 1} ({api_key[:20]}...)")
        return ChatGoogleGenerativeAI(
            model=self.current_model,
            google_api_key=api_key,
            temperature=0.0,
            convert_system_message_to_human=True,
            max_retries=0,  # <--- Forces it to fail instantly so we can handle it properly!\
            request_timeout=200
        )

    def rotate_key(self):
        """Moves to the next key."""
        if self.current_key_index < len(self.keys) - 1:
            self.current_key_index += 1
            print(f"   🔄 Key/Quota Issue! Switching to Key #{self.current_key_index + 1}...")
            return True
        return False

ingestor = SmartIngestor(API_KEYS)

def get_processed_files():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def mark_as_processed(filename):
    with open(LOG_FILE, "a") as f:
        f.write(f"{filename}\n")

async def process_all_pdfs():
    print(f"Scanning PDFs in: {PDF_DIR}")
    
    all_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    processed = get_processed_files()
    files_to_do = [f for f in all_files if f not in processed]
    
    print(f"Total: {len(all_files)} | Remaining: {len(files_to_do)}")
    
    for index, filename in enumerate(files_to_do):
        file_path = os.path.join(PDF_DIR, filename)
        print(f"\n[{index+1}/{len(files_to_do)}] Processing: {filename}...")
        
        # RETRY LOOP
        while True:
            try:
                # 1. Read PDF
                pdf_result = ingestion_service.extract_text_from_pdf(file_path)
                
                # 2. AI Parsing (Using the dynamically updated LLM)
                # manually invoking the chain here to ensure we use the FRESH llm otherwise 
                # the llm_parser will be bonded to exhausted key
                
                parser = PydanticOutputParser(pydantic_object=SyllabusGraph)
                prompt = PromptTemplate(
                    template="""
                    You are an expert Curriculum Designer. Extract a Knowledge Graph.
                    RETURN ONLY JSON.
                    {format_instructions}
                    Syllabus Text:
                    {text}
                    """,
                    input_variables=["text"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                # Create chain with CURRENT key
                chain = prompt | ingestor.get_llm() | parser
                
                print("   Sending to Gemini...")
                # Truncate text to fit context window safely
                structured_data = await chain.ainvoke({"text": pdf_result["raw_text"][:30000]})
                
                # 3. Build Graph
                print("   Building Graph...")
                # Handle cases where Pydantic returns object vs dict
                data_dict = structured_data.dict() if hasattr(structured_data, 'dict') else structured_data
                graph_builder.build_syllabus_graph(data_dict)
                
                # 4. Success
                mark_as_processed(filename)
                print("   Done!")
                
                # MANDATORY SAFETY SLEEP (Do not remove)
                time.sleep(15) 
                break 

            except Exception as e:
                error_str = str(e).lower()
                print(f"  Error: {str(e)[:150]}...")

                # CHECK: Is it a Rate Limit (429) or Quota?
                if "429" in error_str or "resource" in error_str or "quota" in error_str:
                    
                    # Try to find the specific wait time in the error message
                    # Google often says "Please retry in 34s"
                    wait_time = 40 # Default wait
                    match = re.search(r"retry in (\d+)", error_str)
                    if match:
                        wait_time = int(match.group(1)) + 5 # Add buffer
                    
                    print(f"   ⏳ Rate Limit! Sleeping for {wait_time} seconds...")
                    time.sleep(wait_time)
                    
                    # If it's a "Quota" error (Daily limit), rotate immediately
                    # If it's just "Rate Limit" (RPM), the sleep usually fixes it
                    if "quota" in error_str or "resourceexhausted" in error_str: 
                        if not ingestor.rotate_key():
                            print("   ❌ ALL KEYS EXHAUSTED. Exiting.")
                            return
                else:
                    print("   ❌ Non-API Error (e.g., Parsing). Skipping file.")
                    break

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_all_pdfs())