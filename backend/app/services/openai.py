import openai

from fastapi.exceptions import HTTPException
from app.models.chat import Message

from app.config import env
from app.services.chat import get_messages_by_chat


client = openai.OpenAI(
    api_key=env.str("OPENAI_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

async def generate_chatgpt_response(
        message: str | None = None,
        chat_messages: list[Message] | None = None,
        model: str = "qwen-plus"
        ) -> str:
    try:
        if chat_messages is None:
            messages = [
                {"role": "user", "content": message}
                ]
        else:
            # Формируем историю для OpenAI API
            messages = [
                {"role": message.role, "content": message.content}
                for message in chat_messages
            ]
            messages.append({"role": "user", "content": message})
        
        # Отправляем историю в OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages
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
