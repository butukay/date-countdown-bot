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


@router.callback_query(lambda c: c.data.startswith("edit:"))
async def edit_callback_handler(callback_query: types.CallbackQuery) -> None:
    assert callback_query.from_user is not None
    assert callback_query.data is not None

    inline_message_id = callback_query.data.replace("edit:", "")

    user = await users.get_user(callback_query.from_user.id)

    await callback_query.answer("⚠️ Work in progress", show_alert=True)

    # TODO: edit countdown message

    # try:
    #     countdown = user.get_countdown(inline_message_id)
    # except Exception as e:
    #     await callback_query.answer("This countdown doesn't exist")
    #     return

