# core/llm_interface.py
"""Интерфейс для работы с LLM через OpenRouter (DeepSeek)."""
from openai import OpenAI


class LLMInterface:
    def __init__(self, api_key, logger, notifier=None):
        self.logger = logger
        self.notifier = notifier
        self.logger.info("Инициализация OpenRouter (DeepSeek)")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/FadeevIla/Ouroboros",
                "X-Title": "Darwin Self-Evolving Bot",
            },
        )
        self.logger.info("OpenRouter готов")

    def analyze_bugs(self, code):
        self.logger.info("LLM: поиск багов")
        system_prompt = (
            "Ты — senior Python-разработчик. Исправь ВСЕ баги в коде телеграм-бота на aiogram 2.25.1.\n\n"
            "ЧТО ДЕЛАТЬ:\n"
            "1. Если команда содержит ТОЛЬКО pass или заглушку ('статистика бота') — РЕАЛИЗУЙ её.\n"
            "2. Для stats: подсчитай количество команд и верни реальную информацию.\n"
            "3. Для whatsnew: используй модуль core.update_notifier (get_update_description, format_update_message).\n"
            "4. Для weather: проверь наличие OPENWEATHERMAP_API_KEY в os.environ, если нет — предложи пользователю добавить ключ.\n"
            "5. Все reply_text замени на reply или answer.\n"
            "6. Убери skip_updates=True.\n"
            "7. НЕ удаляй импорты из core.\n\n"
            "Верни ПОЛНЫЙ исправленный код. Без markdown."
        )

        return self._call(code, system_prompt, temperature=0.2)

    def generate_feature(self, code):
        self.logger.info("LLM: генерация фичи")
        system_prompt = (
            "Ты — креативный разработчик телеграм-ботов на aiogram 2.25.1.\n"
            "Твоя задача — добавить ОДНУ новую, ПОЛНОСТЬЮ РАБОЧУЮ команду.\n\n"
            "ПРАВИЛА:\n"
            "1. Команда должна делать что-то ПОЛЕЗНОЕ, а не просто возвращать текст-заглушку.\n"
            "2. Если команда требует внешних данных — используй модули из стандартной библиотеки "
            "(random, datetime, json, os.environ).\n"
            "3. НЕ используй внешние API, если их ключ не указан в os.environ.\n"
            "4. ВСЕГДА обрабатывай ошибки через try/except с понятным сообщением пользователю.\n"
            "5. Используй ТОЛЬКО aiogram 2.x: message.reply(), message.answer(), НЕ reply_text.\n"
            "6. Запуск: executor.start_polling(dp) без skip_updates.\n"
            "7. НЕ ломай существующие команды. НЕ удаляй импорты.\n\n"
            "ПРИМЕРЫ ХОРОШИХ КОМАНД:\n"
            "- /random — генерирует случайное число в заданном диапазоне\n"
            "- /coin — подбрасывает монетку (орёл/решка)\n"
            "- /timer N — ставит таймер на N минут и присылает уведомление\n"
            "- /dice — бросает кубик со случайным результатом\n"
            "- /echo текст — повторяет твоё сообщение\n"
            "- /roll N — бросает N-гранный кубик\n\n"
            "Верни ПОЛНЫЙ код с новой фичей. Без markdown."
        )
        return self._call(code, system_prompt, temperature=1.0)

    def _call(self, code, system_prompt, temperature):
        import time

        max_code_len = 4000
        if len(code) > max_code_len:
            code = code[:3000] + "\n# ... середина пропущена ...\n" + code[-1000:]

        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Код bot.py:\n\n{code}"},
                    ],
                    model="google/gemini-2.0-flash-001:free",
                    temperature=temperature,
                    max_tokens=3000,
                )
                result = self._clean(chat.choices[0].message.content)
                tokens = chat.usage.total_tokens if hasattr(chat, "usage") else "?"
                self.logger.info(f"LLM ответ: {len(result)} символов, {tokens} токенов")
                return result
            except Exception as e:
                error_str = str(e)
                # Рейт-лимит или модель перегружена — ждём и пробуем снова
                if "429" in error_str or "rate" in error_str.lower():
                    wait_time = (attempt + 1) * 30
                    self.logger.warning(f"Рейт-лимит, жду {wait_time} сек (попытка {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                # Модель недоступна — пробуем другую
                elif "404" in error_str or "not found" in error_str.lower():
                    self.logger.warning(f"Модель недоступна, пробую запасную (попытка {attempt + 1}/{max_retries})")
                    # На второй попытке пробуем другую бесплатную модель
                    if attempt == 0:
                        time.sleep(10)
                        continue  # попробуем ещё раз ту же
                    elif attempt == 1:
                        # Меняем модель на запасную
                        self.logger.info("Переключаюсь на запасную модель...")
                        try:
                            chat = self.client.chat.completions.create(
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": f"Код bot.py:\n\n{code}"},
                                ],
                                model="meta-llama/llama-3.3-70b-instruct:free",
                                temperature=temperature,
                                max_tokens=3000,
                            )
                            result = self._clean(chat.choices[0].message.content)
                            return result
                        except Exception as e2:
                            self.logger.warning(f"Запасная модель тоже не сработала: {e2}")
                            time.sleep(30)
                else:
                    self.logger.error(f"LLM error: {e}")
                    if self.notifier:
                        self.notifier.send(f"❌ Ошибка LLM: {error_str[:200]}", "error")
                    raise

        raise Exception("Исчерпаны попытки вызова LLM")

    @staticmethod
    def _clean(raw):
        """Очищает вывод LLM от markdown-обёрток и лишних пояснений."""
        cleaned = raw.strip()

        # Убираем markdown-обёртку ```python ... ```
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Убираем первую строку (```python или ```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Убираем последнюю строку (```), если она есть
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        # DeepSeek R1 иногда добавляет пояснения перед кодом
        # Ищем начало Python-кода (import или from)
        lines = cleaned.split("\n")
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ", "#!", "#!/")):
                start_idx = i
                break
            # Пропускаем пояснения вида "Вот исправленный код:" и пустые строки
            if stripped and not stripped.startswith(
                ("Вот", "Here", "Конечно", "Sure", "Исправленный", "Corrected")
            ):
                continue

        if start_idx > 0:
            cleaned = "\n".join(lines[start_idx:])

        return cleaned