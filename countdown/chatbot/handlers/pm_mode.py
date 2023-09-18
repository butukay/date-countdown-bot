from aiogram import types

from aiogram.dispatcher.router import Router

from aiogram.filters import CommandStart
from aiogram import F

from countdown.chatbot import bot
from countdown.data import users

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    assert message.from_user is not None

    if users.is_registered(message.from_user.id):
        await message.answer("You are already registered")
        return

    await message.answer(f"""
👋 <b>Hi! I'm Countdown Bot!</b>

Inline usage:
<code>{bot.me.username} some text %%2024-02-03%% some text</code>

Made with ❤️ by @butukay
""")


@router.message(F.text == "/info")
async def info_handler(message: types.Message) -> None:
    await message.answer(f"""
Inline usage:
<code>@{(await bot.me()).username} some text %%2024-02-03%% some text</code>

Made with ❤️ by @butukay
""")

@router.message(F.text == "/help")
async def help_handler(message: types.Message) -> None:
    await message.answer(f"""
Inline usage:
<code>@{(await bot.me()).username} some text %%2024-02-03%% some text</code>

Made with ❤️ by @butukay
""")

# @router.edited_message(lambda m: m.text.startswith("Until"))
# async def generated_message_handler(message: types.Message) -> None:
#     await message.answer("✅ It works! Now this message will be automatically updated")
