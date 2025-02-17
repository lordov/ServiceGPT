import openai
from fastapi.exceptions import HTTPException
from app.config import env

client = openai.OpenAI(api_key=env.str("OPENAI_API_KEY"))

def generate_chatgpt_response(messages: list[str], model: str = "gpt-3.5-turbo") -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}
                      for message in messages]
        )
        return response.choices[0].message.content
    except openai.RateLimitError as e:
        raise HTTPException(
            429,
            detail=f"OpenAI API rate limit exceeded: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while communicating with OpenAI: {e}")
