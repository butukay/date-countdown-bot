from aiogram import types

from aiogram.dispatcher.router import Router

from aiogram.filters import Command, CommandStart

from countdown.chatbot import bot

from countdown.const import VERSION, GITHUB_URL
# from countdown.data import users

from countdown.locale import Locale, __

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    assert message.from_user is not None

    _ = lambda locale_str: __(Locale(message.from_user.language_code), locale_str)

    # if await users.is_registered(message.from_user.id):
    #     await message.answer("You are already registered")
    #     return
    #
    # await users.register_user(
    #     user_id=message.from_user.id,
    #     username=message.from_user.username
    # )

    await message.answer(
        _("command.start").format(
            bot_username=(await bot.me()).username,
            github_url=GITHUB_URL),
        disable_web_page_preview=True
    )

@router.message(Command(commands=["info", "help"]))
async def info_handler(message: types.Message) -> None:
    assert message.from_user is not None

    _ = lambda locale_str: __(Locale(message.from_user.language_code), locale_str)

    await message.answer(
        _("command.info").format(
            version=VERSION,
            bot_username=(await bot.me()).username,
            github_url=GITHUB_URL),
        disable_web_page_preview=True
    )


# @router.edited_message(lambda m: m.text.startswith("Until"))
# async def generated_message_handler(message: types.Message) -> None:
#     await message.answer("✅ It works! Now this message will be automatically updated")

