from aiogram import Bot, Dispatcher

from aiogram.fsm.strategy import FSMStrategy

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

import threading, asyncio
import logging, sys, os

BOT_TOKEN = os.environ["BOT_TOKEN"]

# ADMIN_CHAT_ID = os.environ['ADMIN_CHAT_ID']

if '--no-state-db' in sys.argv:
    storage = MemoryStorage()
else:
    host     = os.environ.get("STATEDB_HOST", "localhost")
    port     = os.environ.get("STATEDB_PORT", "6379")

    username = os.environ.get("STATEDB_USER")
    password = os.environ.get("STATEDB_PASS")

    if all((username, password)):
        redis_url = f"redis://{username}:{password}@{host}:{port}"
    else:
        redis_url = f"redis://{host}:{port}"

    storage = RedisStorage.from_url(redis_url, key_builder=DefaultKeyBuilder(with_bot_id=True))

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.CHAT)

bot_event_loop = asyncio.new_event_loop()

background_tasks = set()

def chatbot():
    asyncio.set_event_loop(bot_event_loop)

    from countdown.chatbot.handlers import router
    dp.include_router(router)

    # if "--no-start-msg" not in sys.argv:
    #     from countdown.chatbot.logic.admin_logs import send_bot_started
    #     send_bot_started(sys.argv)
    #
    # if "--no-my-commands" not in sys.argv or "--delete-my-commands" not in sys.argv:
    #     from countdown.chatbot.logic.my_commands import send_my_commands
    #     send_my_commands()
    #
    # if "--delete-my-commands" in sys.argv:
    #     from countdown.chatbot.logic.my_commands import delete_my_commands
    #     delete_my_commands()

    task = bot_event_loop.create_task( dp.start_polling(bot, handle_signals=False) )
    background_tasks.add(task)

    bot_event_loop.run_forever()


### called from root main.py
def start():
    logging.info("Setting up chatbot...")

    if '--no-state-db' in sys.argv:
        logging.info("Using in-memory FSM storage")

    try:
        chatbot_thread = threading.Thread(target=chatbot, name="CHATBOT", daemon=True)
        chatbot_thread.start()

        logging.info("Chatbot thread started")
    except Exception as e:
        logging.exception(f"Unable to start chatbot thread: {e}")
