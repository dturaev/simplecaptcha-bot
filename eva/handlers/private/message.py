from aiogram import Bot, Router
from aiogram.filters.command import Command, CommandStart
from aiogram.types import Message

from eva.misc.kb_generators import generate_invite_bot_keyboard
from eva.misc.settings_reader import Settings

router = Router()


@router.message(CommandStart())
async def handle_start_command(message: Message, bot: Bot, settings: Settings) -> None:
    # We can add another parameter `settings` and it magically works.
    # What is this sorcery, "dependency injection"?
    # https://docs.aiogram.dev/en/latest/dispatcher/dependency_injection.html
    # Also, we should probably write middleware to limit access to handlers.
    if message.from_user.id not in settings.ADMINS:
        return
    text = (
        "Привет! У вас есть проблема с ботами-спамерами в чате?\n"
        "У меня есть решение - captcha.\n\n"
        "Я буду проверять всех новые заявки в вашем чате на наличие спамеров.\n"
        "Для того, чтобы начать, выполните следующие действия:\n"
        "1. Перейдите в настройки чата и включите вступление по заявкам\n"
        "Тип чата > Заявки на вступление\n"
        "2. Нажмите на кнопку ниже, чтобы добавить меня в чат\n"
        "3. Следуйте моим дальнейшим инструкциям"
    )
    bot_user = await bot.get_me()
    markup = generate_invite_bot_keyboard(bot_username=bot_user.username)
    await message.answer(text, reply_markup=markup)


@router.message(Command(commands=["privacy"]))
async def handle_privacy_command(message: Message, settings: Settings) -> None:
    # text = f"Privacy Policy:\n{settings.bot.privacy_policy_link}"
    # await message.answer(text)
    return


@router.message(Command(commands=["ping"]))
async def handle_ping_command(message: Message, settings: Settings) -> None:
    text = "pong"
    await message.answer(text)
    return
