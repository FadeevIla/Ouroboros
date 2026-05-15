async def main():
    """Точка входа."""
    if BOT_TOKEN == "твой_токен_бота":
        logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
        logger.error("   Добавь токен в secrets GitHub: Settings → Secrets → TELEGRAM_BOT_TOKEN")
        sys.exit(1)

    logger.info("🔧 Создание приложения...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("about", about))

    logger.info("✅ Бот готов к запуску!")
    logger.info("📋 Команды: /start, /help, /status, /about")

    # Запускаем поллинг
    try:
        await app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())