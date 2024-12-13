from countdown.chatbot import bot, bot_event_loop

from aiogram.types import BotCommand, BotCommandScopeDefault

import asyncio

def send_my_commands():
    asyncio.run_coroutine_threadsafe(
        bot.set_my_commands(
            commands=[
                BotCommand(command="help", description="💬 Show help message"),
            ],
            scope=BotCommandScopeDefault()
        ),
        bot_event_loop
    )

def delete_my_commands():
    asyncio.run_coroutine_threadsafe(
        bot.delete_my_commands(),
        bot_event_loop
    )

