from fastapi import APIRouter
import os
import google.generativeai as genai

router = APIRouter()

@router.get("/llm")
def health_llm():
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"status": "error", "message": "GOOGLE_API_KEY not found"}
            
        genai.configure(api_key=api_key)
        # Use a fast model for the health check
        model_name = os.getenv("LLM_CLASSIFICATION_MODEL", "gemini-2.5-flash")
        model = genai.GenerativeModel(model_name)
        
        # Simple 1-token generation to verify auth
        response = model.generate_content("Hi", generation_config={"max_output_tokens": 5})
        
        if response and response.text:
            return {"status": "ok", "model": model_name}
        else:
            return {"status": "error", "message": "Empty response from Gemini"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
