from aiogram import types

from aiogram.dispatcher.router import Router

from aiogram.filters import Command, CommandStart

from countdown.chatbot import bot

from countdown.const import VERSION, GITHUB_URL
from countdown.data import users

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    assert message.from_user is not None

    # if await users.is_registered(message.from_user.id):
    #     await message.answer("You are already registered")
    #     return
    #
    # await users.register_user(
    #     user_id=message.from_user.id,
    #     username=message.from_user.username
    # )

    await message.answer(f"""
👋 <b>Hello! I'm Countdown Bot!</b>

I can create auto updated messages in your chats, so you can easily track how much time is left until some event.

To create a countdown, start typing a message in one of the folowing formats:
@{(await bot.me()).username} %%2024-02-03%% some text
@{(await bot.me()).username} %%2024-02-03 06:30%% some text

@{(await bot.me()).username} some text [[2024-02-03]] some text
@{(await bot.me()).username} some text [[2024-02-03 06:30]] some text

Made with ❤️ by @butukay • <a href='{GITHUB_URL}'>GitHub</a>
""", disable_web_page_preview=True)


@router.message(Command(commands=["info", "help"]))
async def info_handler(message: types.Message) -> None:
    await message.answer(f"""
⏰ <b>Date Countdown Bot</b>

<b>Version:</b> {VERSION} ✅

To create a countdown, start typing a message in one of the folowing formats:
@{(await bot.me()).username} %%2024-02-03%% some text
@{(await bot.me()).username} %%2024-02-03 06:30%% some text

@{(await bot.me()).username} some text [[2024-02-03]] some text
@{(await bot.me()).username} some text [[2024-02-03 06:30]] some text

Made with ❤️ by @butukay • <a href='{GITHUB_URL}'>GitHub</a>
""", disable_web_page_preview=True)


# @router.edited_message(lambda m: m.text.startswith("Until"))
# async def generated_message_handler(message: types.Message) -> None:
#     await message.answer("✅ It works! Now this message will be automatically updated")

