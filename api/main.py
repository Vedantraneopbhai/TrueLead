import os
import sys
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.explain import explain_prediction, get_explainability_engine
from src.ocr_processor import extract_text_from_image

app = FastAPI(
    title="TrueLead / SachHai - Fake Job Scam Detector API",
    description="Multimodal, Multi-language Fake Job Posting Scam Risk API with Explainable AI & Domain Reputation Checks",
    version="2.0.0"
)

# Global engine instance
explain_engine = None

class JobPostingRequest(BaseModel):
    text: str
    company: Optional[str] = ""
    title: Optional[str] = ""

class ScoreResponse(BaseModel):
    score: int
    confidence: str
    flags: List[str]
    categorized_flags: Dict[str, List[str]]
    detected_language: str
    domain_info: Dict[str, Any]
    shap_features: List[Dict[str, Any]]
    extracted_text: Optional[str] = None
    report: Optional[Dict[str, Any]] = None

def get_engine():
    global explain_engine
    if explain_engine is None:
        explain_engine = get_explainability_engine()
    return explain_engine

@app.on_event("startup")
def load_engine():
    get_engine()

@app.get("/health")
def health_check():
    engine = get_engine()
    return {"status": "ok", "engine_loaded": engine is not None}

@app.post("/score", response_model=ScoreResponse)
def score_job_posting(request: JobPostingRequest):
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Job posting text cannot be empty.")
        
    engine = get_engine()
    result = explain_prediction(
        text=request.text,
        company=request.company or "",
        title=request.title or "",
        engine=engine
    )
    return result

@app.post("/score-image", response_model=ScoreResponse)
async def score_job_image(
    file: UploadFile = File(...),
    company: Optional[str] = Form("")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image (PNG, JPG, JPEG, WEBP).")
        
    try:
        contents = await file.read()
        extracted_text, success, err_msg = extract_text_from_image(contents)
        
        if not success:
            return ScoreResponse(
                score=50,
                confidence="Needs Review",
                flags=[f"OCR Warning: {err_msg}"],
                categorized_flags={"fee": [], "urgency": [], "contact": [], "domain": [], "salary": []},
                detected_language="Unknown",
                domain_info={"domain_count": 0, "has_recent_domain": 0, "has_typosquat": 0, "has_free_email": 0, "company_domain_mismatch": 0, "flags": []},
                shap_features=[],
                extracted_text=err_msg
            )
            
        engine = get_engine()
        result = explain_prediction(
            text=extracted_text,
            company=company or "",
            engine=engine
        )
        result['extracted_text'] = extracted_text
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.get("/download-extension")
def download_extension():
    import zipfile
    import io
    from fastapi.responses import StreamingResponse

    ext_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extension")
    if not os.path.exists(ext_dir):
        raise HTTPException(status_code=404, detail="Extension directory not found.")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(ext_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, ext_dir)
                zip_file.write(file_path, arcname)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=truelead-chrome-extension.zip"}
    )

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "TrueLead API v2.0 is running."}
