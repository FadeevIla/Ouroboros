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
            "Ты — senior Python-разработчик. Исправь ВСЕ баги в коде телеграм-бота.\n"
            "Бот написан на aiogram версии 2.25.1.\n\n"
            "ВАЖНЫЕ ПРАВИЛА aiogram 2.x:\n"
            "- У сообщений НЕТ метода reply_text. Используй message.reply() или message.answer()\n"
            "- Импорты: from aiogram import Bot, Dispatcher, types\n"
            "- Типы: from aiogram.types import Message, CallbackQuery\n"
            "- НЕ используй Update из aiogram.types (его нет в aiogram 2.x)\n"
            "- Используй message.reply(), НЕ message.reply_text()\n\n"
            "НЕ трогай импорты из core.*.\n"
            "НЕ удаляй строку from core import environ_map — она нужна.\n"
            "Верни ПОЛНЫЙ исправленный код. Без объяснений, без markdown."
        )

        return self._call(code, system_prompt, temperature=0.2)

    def generate_feature(self, code):
        self.logger.info("LLM: генерация фичи")
        system_prompt = (
            "Ты — разработчик телеграм-ботов. Добавь одну новую команду в бота.\n"
            "Бот написан на aiogram версии 2.25.1. ПРАВИЛЬНЫЕ импорты:\n"
            "from aiogram import Bot, Dispatcher, types\n"
            "from aiogram.types import Message, CallbackQuery, Update\n\n"
            "НЕ используй Application, filters, handlers из aiogram 3.x.\n"
            "НЕ ломай существующие команды. НЕ добавляй os.system, subprocess, eval, exec.\n"
            "НЕ трогай импорты core.*.\n"
            "Верни ПОЛНЫЙ код с новой фичей. Без объяснений, без markdown."
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