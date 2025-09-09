from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
import json
from typing import List
from resume_final import process_resume
import uvicorn

app = FastAPI(title="AI Resume Parser API", version="1.0.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Resume Parser API is running", "status": "active"}

@app.post("/parse-resume")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """
    Parse a single resume file and return extracted information
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.txt', '.rtf')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload PDF, DOCX, TXT, or RTF files."
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process the resume using our improved parser
            result_json = process_resume(tmp_file_path)
            result_data = json.loads(result_json)
            
            # Add metadata
            result_data["metadata"] = {
                "filename": file.filename,
                "file_size": len(content),
                "processing_status": "success"
            }
            
            return JSONResponse(content=result_data)
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "processing_status": "failed",
                "metadata": {
                    "filename": file.filename if file else "unknown",
                    "file_size": 0
                }
            }
        )

@app.post("/parse-multiple")
async def parse_multiple_resumes(files: List[UploadFile] = File(...)):
    """
    Parse multiple resume files and return results for each
    """
    results = []
    
    for file in files:
        try:
            # Validate file type
            if not file.filename.lower().endswith(('.pdf', '.docx', '.txt', '.rtf')):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "Unsupported file type",
                    "data": None
                })
                continue
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            try:
                # Process the resume
                result_json = process_resume(tmp_file_path)
                result_data = json.loads(result_json)
                
                # Transform the data to match frontend expectations
                personal_info = result_data.get("personalInfo", {})
                transformed_data = {
                    "name": personal_info.get("name"),
                    "email": personal_info.get("email"),
                    "phone": personal_info.get("phone"),
                    "location": personal_info.get("location"),
                    "linkedin": personal_info.get("linkedin"),
                    "github": personal_info.get("github"),
                    "skills": result_data.get("skills", []),
                    "total_experience": result_data.get("total_experience", "0 years and 0 months"),
                    "summary": result_data.get("summary", ""),
                    "experience": result_data.get("experience", ""),
                    "education": result_data.get("education", "")
                }
                
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "data": transformed_data,
                    "error": None
                })
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e),
                "data": None
            })
    
    return JSONResponse(content={"results": results})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "AI Resume Parser is operational"}

if __name__ == "__main__":
    print("🚀 Starting AI Resume Parser API...")
    print("📡 Frontend should connect to: http://127.0.0.1:8080")
    print("🔗 API Documentation: http://127.0.0.1:8080/docs")
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8080,
        reload=False,  # Fixed: disable reload when running directly
        log_level="info"
    )
