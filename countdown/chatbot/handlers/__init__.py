import aiogram
from aiogram import types

from aiogram.dispatcher.router import Router

from . import inline_mode
from . import pm_mode

from . import edit_countdown

router = Router()
router.include_router(inline_mode.router)
router.include_router(pm_mode.router)

router.include_router(edit_countdown.router)

unknown_command_router = Router()

@unknown_command_router.message()
async def unknown_message_handler(message: types.Message):
    if message.chat.type != aiogram.enums.ChatType.PRIVATE:
        return

    if message.via_bot is not None:
        return

    await message.answer("Unknown command, try /help")

router.include_router(unknown_command_router)
