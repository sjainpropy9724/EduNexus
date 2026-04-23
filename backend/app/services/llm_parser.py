from pydantic import BaseModel, Field
from typing import List
from app.core.llm_manager import key_manager
import json
import re

# ── Pydantic Models (unchanged — graph_builder depends on these) ──────────────

class SyllabusConcept(BaseModel):
    concept_name: str = Field(description="Name of the technical concept, e.g., 'Neural Networks'")
    category: str = Field(description="Broader category, e.g., 'Deep Learning'")
    prerequisites: List[str] = Field(description="List of implied prerequisites, e.g., ['Linear Algebra']")

class SyllabusGraph(BaseModel):
    course_title: str = Field(description="The main title of the course")
    concepts: List[SyllabusConcept] = Field(description="List of all extracted concepts")

# ── Improved Prompt ───────────────────────────────────────────────────────────

SYLLABUS_PROMPT = """You are an expert Curriculum Designer and Knowledge Graph Engineer.

Your task is to analyze a university course syllabus and extract a structured knowledge graph.

INSTRUCTIONS:
1. Identify the exact Course Title from the document header
2. Extract EVERY distinct technical concept, tool, algorithm, framework, or methodology mentioned
3. For each concept, assign a broad Category (e.g., "Machine Learning", "Web Development", "Databases")
4. For each concept, list its direct Prerequisites — concepts that must be understood BEFORE this one
   - Only list prerequisites that are genuinely required (not just related)
   - Prerequisites do NOT need to be mentioned in the syllabus — infer from domain knowledge
   - Use standard canonical names for prerequisites (e.g., "Python" not "Python programming language")

RULES:
- Extract 15-40 concepts per syllabus (not too sparse, not every sentence)
- concept_name must be a specific technical term, not a vague phrase like "Introduction to X"
- prerequisites list can be empty [] if the concept is foundational
- Return ONLY valid JSON, no markdown, no explanation, no preamble

OUTPUT FORMAT (return exactly this structure):
{
  "course_title": "string",
  "concepts": [
    {
      "concept_name": "string",
      "category": "string", 
      "prerequisites": ["string", "string"]
    }
  ]
}

SYLLABUS TEXT:
{text}"""

# ── Service ───────────────────────────────────────────────────────────────────

class LLMParserService:

    async def extract_graph_data(self, raw_text: str) -> dict:
        """
        Uses Claude to convert raw syllabus text into a Structured Graph Schema.
        Returns a dict matching SyllabusGraph schema.
        """
        safe_text = raw_text[:25000]  # ~6k tokens, well within limits
        
        try:
            print(f"⏳ Sending syllabus to Claude ({key_manager.get_model()})...")
            
            message = key_manager.get_client().messages.create(
                model=key_manager.get_model(),
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": SYLLABUS_PROMPT.format(text=safe_text)
                    }
                ]
            )
            
            raw_response = message.content[0].text.strip()
            print("✅ Claude extraction successful!")
            
            # Clean response — strip any accidental markdown fences
            clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_response, flags=re.MULTILINE).strip()
            
            # Parse and validate with Pydantic
            parsed = json.loads(clean)
            validated = SyllabusGraph(**parsed)
            return validated.dict()
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}\nRaw response: {raw_response[:300]}")
            return {"error": f"JSON parse failed: {str(e)}"}
        except Exception as e:
            print(f"❌ Claude API error: {e}")
            return {"error": str(e)}

llm_service = LLMParserService()
