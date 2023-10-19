from countdown.chatbot import dp, bot, bot_event_loop

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from countdown.data import users

from dataclasses import dataclass
from typing import Callable, Coroutine

import traceback
import datetime
import asyncio
import json
import time

import logging
log = logging.getLogger(__name__)

executed_mailings = json.load(open("data/executed_mailings.json", "r"))

@dataclass
class Mailing:
    id: str

    execute_once: bool # execute this mailing only once and dont send it to new users

    run_once: bool # run function only once independently of result
    send_once: bool # stop executing function if result is True once

    # async function with one argument user whitch returns bool
    func: Callable[[users.User], Coroutine]

    disabled: bool

    def execute(self, users: list[users.User]):
        if self.disabled: return

        if self.execute_once:
            if self.id in executed_mailings:
                return

        for user in users:
            try:
                self.run(user)
            except Exception as e:
                log.exception(f"Error while processing mailing func: {e}")
                time.sleep(3)

        if self.id not in executed_mailings:
            executed_mailings[self.id] = datetime.datetime.now().isoformat()
            json.dump(executed_mailings, open("data/executed_mailings.json", "w"))


    def run(self, user: users.User):
        if self.id in user.mailings_done:
            return

        result = asyncio.run_coroutine_threadsafe(
            self.func(user),
            bot_event_loop
        ).result()

        if self.execute_once or self.run_once or (self.send_once and result):
            user.mailings_done.append(self.id)

        if result:
            time.sleep(1)


MAILING: list[Mailing] = []

def mailing_func(id: str, execute_once: bool = False, run_once: bool = False, send_once: bool = False, disabled: bool = False):
    def wrapper(func):
        MAILING.append(
            Mailing(id=id, execute_once=execute_once, run_once=run_once, send_once=send_once, func=func, disabled=disabled)
        )

    return wrapper


@mailing_func(id="update_v1", execute_once=True, send_once=True, disabled=True)
async def send_connect_demo_1(user: users.User):
    if user.registered < datetime.datetime(2023, 10, 18):
        return False

    await bot.send_message(user.user_id, """
⏰ <b>Sorry for downtime</b> ⏰

I did not expect that the bot would become so popular and I would have to pay for the server. I will try to fix everything and release an update as soon as possible.
""")


async def run_mailing_async():
    log.info("Running mailing...")
    time_start = time.time()

    async for user in users.get_users_async_iterable():
        for mailing in MAILING:
            mailing.execute([user])

        await users.save_user(user)

    log.info(f"Mailing executed in: {time.time() - time_start:.4f} сек")


def run_mailing():
    asyncio.run(
        run_mailing_async()
    )

