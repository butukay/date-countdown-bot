from typing import List, AsyncIterable, Iterable

from countdown.data.database import get_users_collection

from .countdown import DefaultCountdown, FormattedCountdown

import pydantic
import datetime

class User(pydantic.BaseModel):
    user_id: int
    username: str | None = None

    registered: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    mailings_done: List[str] = pydantic.Field(default_factory=list)

    countdowns: List[DefaultCountdown | FormattedCountdown] = pydantic.Field(default_factory=list)

    def add_countdown(self, countdown: DefaultCountdown | FormattedCountdown) -> None:
        self.countdowns.append(countdown)

    def update_countdown(self, countdown: DefaultCountdown | FormattedCountdown) -> None:
        for i in range(len(self.countdowns)):
            if self.countdowns[i].inline_message_id == countdown.inline_message_id:
                self.countdowns[i] = countdown
                return

    def __repr__(self) -> str:
        if self.username:
            return f"User {self.username} (id: {self.user_id})"
        else:
            return f"User {self.user_id}"

    def __str__(self) -> str:
        return self.__repr__()


async def get_user(user_id: int) -> User:
    collection = get_users_collection()
    user = await collection.find_one({'user_id': user_id})

    if user is None:
        raise ValueError(f'User with user_id {user_id} not found')

    return User(**user)


async def get_users_async_iterable() -> AsyncIterable[User]:
    collection = get_users_collection()

    async for user in collection.find():
        yield User(**user)


async def get_users_list() -> list[User]:
    collection = get_users_collection()
    users = collection.find()

    users_list = []
    async for user in users:
        users_list.append(User(**user))

    return users_list


async def is_registered(user_id: int) -> bool:
    try:
        await get_user(user_id)
    except ValueError:
        return False

    return True


async def save_user(user: User) -> None:
    collection = get_users_collection()
    await collection.replace_one({'user_id': user.user_id, 'user_id': user.user_id}, user.model_dump(mode="json"))


async def save_users(users: Iterable[User]) -> None:
    collection = get_users_collection()
    for user in users:
        await collection.replace_one({'user_id': user.user_id, 'user_id': user.user_id}, user.model_dump(mode="json"))


async def register_user(user_id: int, username: str | None) -> User:
    collection = get_users_collection()

    new_user = User(
        user_id=user_id,
        username=username or "#N/A"
    )

    await collection.insert_one(new_user.model_dump(mode="json"))

    return new_user


async def delete_user(user_id: int) -> None:
    collection = get_users_collection()
    await collection.delete_one({'user_id': user_id})


async def get_countdown(inline_message_id: str) -> tuple[User, DefaultCountdown | FormattedCountdown]:
    async for user in get_users_async_iterable():
        for countdown in user.countdowns:
            if countdown.inline_message_id == inline_message_id:
                return user, countdown

    raise ValueError(f"Countdown with inline_message_id {inline_message_id} not found")


async def save_countdown(countdown: DefaultCountdown | FormattedCountdown) -> None:
    user, _ = await get_countdown(countdown.inline_message_id)
    user.update_countdown(countdown)
    await save_user(user)

