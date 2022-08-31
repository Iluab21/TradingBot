from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


# Ограничение доступа посторонних пользователей к нашему боту
class Middleware(BaseMiddleware):
    def __init__(self, access_id: int):
        self.access_id = access_id
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if int(message.from_user.id) != int(self.access_id):
            await message.answer("Access Denied")
            raise CancelHandler()

    async def on_process_callback(self, callback_query: types.CallbackQuery, _):
        if int(callback_query.from_user.id) != int(self.access_id):
            await callback_query.answer("Access Denied")
            raise CancelHandler()
