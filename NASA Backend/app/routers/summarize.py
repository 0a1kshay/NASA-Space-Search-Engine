from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv

from app.models import SummarizeRequest, SummaryResponse

# Load environment variables
load_dotenv()

# Initialize OpenAI client if API key is available
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = None

if openai_api_key:
    try:
        import openai
        openai_client = openai.OpenAI(api_key=openai_api_key)
    except ImportError:
        pass
    except Exception as e:
        print(f"Error initializing OpenAI client: {str(e)}")

router = APIRouter(
    prefix="/summarize",
    tags=["summarize"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=SummaryResponse)
async def summarize_text(request: SummarizeRequest):
    """
    Generate an AI summary of the provided text.
    
    Parameters:
        request (SummarizeRequest): The text to summarize and optional max length.
        
    Returns:
        SummaryResponse: The AI-generated summary.
    """
    try:
        text = request.text
        max_length = request.max_length

        # If text is too short, just return it
        if len(text.split()) < 20:
            return {"summary": text}

        # Use OpenAI if available
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a scientific research assistant specialized in space biology. Summarize the following text concisely."},
                        {"role": "user", "content": f"Please summarize this text in {max_length} words or less:\n\n{text}"}
                    ],
                    max_tokens=max_length * 4,  # Approximate token count
                    temperature=0.5,
                )
                summary = response.choices[0].message.content.strip()
                return {"summary": summary}
            except Exception as e:
                print(f"OpenAI API error: {str(e)}")
                # Fall back to placeholder method
        
        # Placeholder summarization method
        words = text.split()
        if len(words) > max_length:
            summary = " ".join(words[:max_length]) + "..."
        else:
            summary = text
        
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")