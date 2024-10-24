from aiogram.types import User


def user_repr(user: User) -> str:
    return f"{user.id} ({user.full_name}, @{user.username})"
