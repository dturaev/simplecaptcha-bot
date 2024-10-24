from aiogram import Bot, Router, types
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter

from eva.misc.loggers import logger
from eva.misc.utils import user_repr

router = Router()

JOIN_TRANSITION = IS_NOT_MEMBER >> IS_MEMBER
LEAVE_TRANSITION = ~JOIN_TRANSITION


@router.chat_member(
    ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION),
)
async def member_joined(update: types.ChatMemberUpdated, bot: Bot) -> None:
    user = update.new_chat_member.user
    logger.warning(f"User {user_repr(user)} joined!")
    text = (
        f"{user.mention_html(user.first_name)}, привет и "
        "филь шпас ☀️ при вопросах загляни в #правила"
    )
    await bot.send_message(chat_id=update.chat.id, text=text)


@router.chat_member(
    ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION),
)
async def member_left(update: types.ChatMemberUpdated, bot: Bot) -> None:
    user = update.old_chat_member.user
    logger.warning(f"User {user_repr(user)} left!")
    # text = "Пока"
    # await bot.send_message(chat_id=update.chat.id, text=text)
