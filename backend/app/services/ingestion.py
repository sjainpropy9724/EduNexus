import pdfplumber
import os
from fastapi import UploadFile
from app.core.config import settings

class PDFIngestionService:

    async def save_upload(self, file: UploadFile, safe_filename: str = None) -> str:
        """Saves uploaded file with optional safe (UUID-prefixed) filename."""
        filename = safe_filename or file.filename
        file_location = os.path.join(settings.UPLOAD_DIR, filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        return file_location

    def extract_text_from_pdf(self, file_path: str) -> dict:
        full_text  = ""
        page_count = 0
        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n\n"
            return {
                "status":   "success",
                "filename": os.path.basename(file_path),
                "pages":    page_count,
                "raw_text": full_text.strip()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

ingestion_service = PDFIngestionService()
