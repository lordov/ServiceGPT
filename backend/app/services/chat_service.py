from fastapi import HTTPException

from app.models.chat import Chat
from app.schemas.chat import ChatOut, MessageSchema, MessageOut, ChatCreate
from app.utils.unit_of_work import IUnitOfWork
from app.core.my_logging import logger
from app.schemas.user import UserOut
from app.services.openai import generate_chatgpt_response
from app.utils.text import get_title
from app.core.exceptions.exceptions import NoRowsFoundError


class ChatService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def create_chat(
            self,
            data: ChatCreate
    ) -> ChatOut:
        async with self.uow:
            chat: Chat = await self.uow.chat.add_one(data.model_dump())
            chat_to_return = ChatOut.model_validate(chat)
            await self.uow.commit()
            logger.info(f"Chat {chat.id} created by user {data.owner_id}")
            return chat_to_return

    async def get_chats_by_user(self, owner_id: int) -> list[ChatOut]:
        async with self.uow:
            try:
                chats = await self.uow.chat.get_all(owner_id=owner_id)
            except NoRowsFoundError:
                return []
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            logger.info(
                f"User {owner_id} fetched their chat list ({len(chats)} chats)")
            return [ChatOut.model_validate(chat) for chat in chats]

    async def create_message(
            self,
            message_data: MessageSchema,
            sender_id: int,
            role: str | None = None
    ) -> MessageOut:
        async with self.uow:
            # Собираем данные для создания сообщения
            data = {
                "chat_id": message_data.chat_id,
                "sender_id": sender_id,
                "content": message_data.content,
                "role": role
            }
            msg: MessageSchema = await self.uow.message.add_one(data)
            await self.uow.commit()
            logger.info(
                f"Message {msg.id} created in chat {msg.chat_id} by user {sender_id}")
            return MessageOut.model_validate(msg)

    async def create_chat_and_send_message(
        self,
        message_data: MessageSchema,
        current_user: UserOut
    ) -> MessageOut:
        # Получаем ответ от нейросети по содержимому сообщения пользователя
        gpt_response = await generate_chatgpt_response(message=message_data.content)
        # Генерируем название чата на основе ответа нейросети
        title = get_title(gpt_response)

        async with self.uow:
            # Создаем новый чат. В ChatCreate owner_id берется из токена (current_user)
            chat_create = ChatCreate(title=title, owner_id=current_user.id)
            chat: Chat = await self.uow.chat.add_one(chat_create.model_dump())

            # Сохраняем сообщение пользователя в созданном чате
            user_message_data = {
                "chat_id": chat.id,
                "content": message_data.content,
                "sender_id": current_user.id,
                "role": "user"
            }
            await self.uow.message.add_one(user_message_data)

            # Сохраняем сообщение от нейросети (бота). Здесь sender_id и role задаются явно.
            bot_message_data = {
                "chat_id": chat.id,
                "content": gpt_response,
                "sender_id": 1,         # Фиксированный ID для бота
                "role": "assistant"
            }
            bot_message = await self.uow.message.add_one(bot_message_data)

            # Фиксируем изменения транзакции
            await self.uow.commit()
            logger.info(
                f"Chat {chat.id} created with user message and bot response for user {current_user.id}"
            )
        # Преобразуем ORM-объект в Pydantic-схему для ответа
        return MessageOut.model_validate(bot_message)

    async def send_message_to_chat(
        self,
        chat_id: int,
        message_data: MessageSchema,
        current_user: UserOut
    ) -> MessageOut:
        async with self.uow:
            # Проверяем, существует ли чат
            chat: Chat = await self.uow.chat.get_one(chat_id)
            if not chat:
                raise HTTPException(status_code=404, detail="Чат не найден")

            # Получаем историю сообщений для формирования контекста (можно ограничить, если нужно)
            chat_messages = await self.uow.message.get_by_chat(chat_id)

            # Генерируем ответ от нейросети, передавая историю сообщений
            gpt_response = await generate_chatgpt_response(
                message_data.content,
                chat_messages=chat_messages
            )

            # Формируем данные для сообщения пользователя
            user_message_data = {
                "chat_id": chat_id,
                "content": message_data.content,
                "sender_id": current_user.id,
                "role": "user"
            }
            await self.uow.message.add_one(user_message_data)

            # Формируем данные для сообщения бота
            bot_message_data = {
                "chat_id": chat_id,
                "content": gpt_response,
                "sender_id": 1,         # Фиксированный ID для бота
                "role": "assistant"
            }
            bot_message = await self.uow.message.add_one(bot_message_data)

            # Фиксируем транзакцию
            await self.uow.commit()

        return MessageOut.model_validate(bot_message)

    async def get_chat_messages(
            self,
            chat_id: int,
            current_user: UserOut
    ) -> list[MessageOut]:
        async with self.uow:
            # Проверяем, существует ли чат
            chat: Chat = await self.uow.chat.get_one(chat_id)
            if not chat or chat.owner_id != current_user.id:
                raise HTTPException(status_code=404, detail="Чат не найден")

            # Получаем список сообщений через репозиторий сообщений
            messages = await self.uow.message.get_by_chat(chat_id)

            # Преобразуем ORM объекты в Pydantic схему
            return [MessageOut.model_validate(message) for message in messages]

    async def delete_chat(self, chat_id: int, current_user: UserOut) -> dict:
        async with self.uow:
            # Получаем чат по идентификатору
            chat = await self.uow.chat.get_one(chat_id)
            if not chat or chat.owner_id != current_user.id:
                logger.warning(
                    f"User {current_user.id} tried to delete non-existing chat {chat_id}"
                )
                raise HTTPException(status_code=404, detail="Chat not found")

            # Удаляем чат
            deleted = await self.uow.chat.delete_one(chat_id)
            if not deleted:
                logger.error(f"Failed to delete chat {chat_id}")
                raise HTTPException(
                    status_code=500, detail="Failed to delete chat")

            await self.uow.commit()
            logger.info(f"User {current_user.id} deleted chat {chat_id}")

        return {"message": "Chat deleted successfully"}
