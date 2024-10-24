import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from eva.handlers import main_router
from eva.misc.configure import configure_logging, configure_services
from eva.misc.settings_reader import Settings
from eva.misc.webhook import configure_app

settings = Settings()

# Improvement ideas
# - Add timeout if captcha wasn't solved correctly
# - Generate captcha pic on the fly
# - Add setting that determines captcha language


async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    services = await configure_services(settings)
    dispatcher.workflow_data.update(services)
    await bot.delete_webhook()
    if settings.webhook.url:
        await bot.set_webhook(
            settings.webhook.url, allowed_updates=dispatcher.resolve_used_update_types()
        )


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()
    await bot.session.close()


async def main() -> None:
    configure_logging()
    bot = Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    try:
        if settings.webhook.url:
            app = configure_app(dp, bot, settings)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(
                runner, host=settings.webapp.host, port=settings.webapp.port
            )
            await site.start()
            await asyncio.Event().wait()
        else:
            await dp.start_polling(bot, settings=settings)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)
