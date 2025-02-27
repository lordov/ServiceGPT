import re


def get_title(text: str, max_length: int = 255) -> str:
    # Используем регулярное выражение для разделения текста на предложения
    # Разделители: точка, вопросительный знак, восклицательный знак + пробел
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Берем первые два предложения
    result = '. '.join(sentences[:2])

    # Если есть знак препинания в конце, добавляем его
    if sentences and sentences[0].endswith(('.', '!', '?')):
        result += sentences[0][-1]

    # Обрезаем результат до max_length символов
    if len(result) > max_length:
        # Находим последний пробел перед max_length для чистого обрезания
        truncated_result = result[:max_length].rsplit(' ', 1)[0]
        return truncated_result + '...'
    return result
