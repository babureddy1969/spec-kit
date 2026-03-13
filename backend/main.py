import os
from datetime import datetime
import json
from google import genai
from google.genai import types
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCS_DIR = "../documents"
VERSIONS_DIR = "../versions"

# Ensure directories exist
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(VERSIONS_DIR, exist_ok=True)

# In-memory document storage
documents_memory = {}

def load_documents():
    """Reads all files under DOCS_DIR into memory."""
    global documents_memory
    documents_memory.clear()
    for filename in os.listdir(DOCS_DIR):
        file_path = os.path.join(DOCS_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                documents_memory[filename] = f.read()

# Load documents on startup
@app.on_event("startup")
async def startup_event():
    load_documents()

@app.get("/documents")
async def get_documents():
    """Returns a list of all document filenames."""
    return {"documents": list(documents_memory.keys())}

@app.get("/documents/{filename}")
async def get_document(filename: str):
    """Returns the content of a specific document."""
    if filename not in documents_memory:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"content": documents_memory[filename]}

class UpdateDocRequest(BaseModel):
    filename: str
    content: str

def save_version(filename: str, old_content: str):
    """Moves the original document to the versions directory with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    base_name, ext = os.path.splitext(filename)
    versioned_filename = f"{base_name}-{timestamp}{ext}"
    versioned_path = os.path.join(VERSIONS_DIR, versioned_filename)
    
    with open(versioned_path, 'w', encoding='utf-8') as f:
        f.write(old_content)
        
    # Remove old file if it actually exists there (it should be overwritten anyway, but just to be clean)
    original_path = os.path.join(DOCS_DIR, filename)
    if os.path.exists(original_path):
        os.remove(original_path)

def save_new_doc(filename: str, new_content: str):
    """Saves new content to documents dir and updates memory."""
    with open(os.path.join(DOCS_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(new_content)
    documents_memory[filename] = new_content

def call_llm_for_updates(updated_filename: str, updated_content: str):
    """Calls Gemini to determine updates to related documents."""
    client = genai.Client() # Expects GEMINI_API_KEY environment variable
    
    # Prepare context for the prompt
    other_docs = {k: v for k, v in documents_memory.items() if k != updated_filename}
    
    prompt = f"""
    You are an intelligent document synchronization system.
    A user has just updated the document '{updated_filename}'.
    
    Here is the NEW content of '{updated_filename}':
    ---
    {updated_content}
    ---
    
    Here are the CURRENT contents of all other related documents in the system:
    {json.dumps(other_docs, indent=2)}
    
    Your task: Analyze the changes in '{updated_filename}'. Determine if any sections in the OTHER documents need to be updated to reflect or align with these new changes.
    Only update documents that logically MUST change based on the new information.
    
    Return a JSON object in the following format:
    {{
        "updates": [
            {{
                "filename": "document_name.txt",
                "new_content": "The full revised content of the document."
            }}
        ]
    }}
    
    IMPORTANT: Return ONLY valid JSON matching this schema. Do not include markdown blocks like ```json.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Clean up response if it has markdown formatting
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        result = json.loads(text_response.strip())
        return result.get("updates", [])
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return []

@app.post("/update-doc")
async def update_doc(request: UpdateDocRequest):
    """Updates a document, saves version, and intelligently updates related docs."""
    filename = request.filename
    new_content = request.content
    
    if filename not in documents_memory:
        raise HTTPException(status_code=404, detail="Document not found")
        
    old_content = documents_memory[filename]
    
    # 1. Save version of the edited file
    save_version(filename, old_content)
    
    # 2. Save the new content (memory + disk)
    save_new_doc(filename, new_content)
    
    # 3. Call LLM to figure out other updates
    related_updates = call_llm_for_updates(filename, new_content)
    
    updated_files = [filename]
    
    # 4. Apply updates manually to related files
    for update in related_updates:
        target_filename = update.get("filename")
        target_new_content = update.get("new_content")
        
        if target_filename and target_filename in documents_memory and target_new_content:
            target_old_content = documents_memory[target_filename]
            save_version(target_filename, target_old_content)
            save_new_doc(target_filename, target_new_content)
            updated_files.append(target_filename)
            
    return {
        "message": f"Successfully updated {filename}",
        "updated_documents": updated_files
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
