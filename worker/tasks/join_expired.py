from typing import Any, Dict

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from eva.misc.loggers import arq_logger as logger
from eva.services.lock_user import LockUserService


async def join_expired_task(
    ctx: Dict[str, Any], chat_id: int, user_id: int, salt: str
) -> None:
    bot: Bot = ctx["bot"]
    lock_user: LockUserService = ctx["lock_user_service"]
    logger.info(f"Checking if user {user_id} in chat {chat_id} passed captcha")
    is_captcha_passed = not await lock_user.is_captcha_target(chat_id, user_id, salt)
    if is_captcha_passed:
        logger.info(f"User {user_id} in chat {chat_id} already passed captcha")
        return
    try:
        await bot.decline_chat_join_request(chat_id, user_id)
        await lock_user.delete_correct_answer(chat_id, user_id, salt)
    except TelegramAPIError as e:
        logger.error(
            f"Error while declining chat join request "
            f"for user {user_id} in chat {chat_id}: {e}"
        )
        return
    logger.info(f"TIMEOUT for ({user_id}) in chat ({chat_id})")
