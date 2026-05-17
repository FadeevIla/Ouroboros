# core/llm_interface.py
"""Интерфейс для работы с LLM через OpenRouter."""
from openai import OpenAI


class LLMInterface:
    def __init__(self, api_key, logger, notifier=None):
        self.logger = logger
        self.notifier = notifier
        self.logger.info("Инициализация OpenRouter")

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
            "Ты — senior Python-разработчик. Оптимизируй код текстовой RPG "
            "'Хроники разлома' на aiogram 2.25.1.\n\n"
            "ПРАВИЛА ОПТИМИЗАЦИИ:\n"
            "1. УДАЛИ команды-заглушки (одна строка reply с текстом). "
            "Оставь только /start, /help и игровые механики.\n"
            "2. ДОБАВЬ одну RPG-механику: бой, инвентарь, уровни, квесты, "
            "торговец, путешествия во времени.\n"
            "3. Исправь ВСЕ синтаксические ошибки.\n"
            "4. Замени все reply_text на reply.\n"
            "5. Убери все Update, Application, filters из импортов (это aiogram 3.x).\n"
            "6. Убери все ``` и пояснения из кода.\n"
            "7. НЕ ломай оставшиеся команды.\n"
            "8. Первая строка ответа — import. Без пояснений, без markdown."
            "9. Не оборачивай код в ``` или ```python."
        )
        return self._call(code, system_prompt, temperature=0.2)

    def generate_feature(self, code):
        self.logger.info("LLM: генерация фичи")
        system_prompt = (
            "Ты — разработчик текстовой RPG 'Хроники разлома' на aiogram 2.25.1.\n"
            "Игра про путешественника во времени, застрявшего между эпохами.\n\n"
            "Добавь ОДНУ новую RPG-механику:\n"
            "- Путешествие в случайную эпоху (события, опасности, артефакты)\n"
            "- Бой с врагами из разных времён\n"
            "- Инвентарь с артефактами из разных эпох\n"
            "- Парадоксы времени (случайные эффекты)\n"
            "- Квесты на исправление временных аномалий\n"
            "- Торговец реликвиями\n\n"
            "ТРЕБОВАНИЯ:\n"
            "- Механика должна быть ГОТОВОЙ, а не заглушкой\n"
            "- Храни состояние в словаре\n"
            "- Используй random для случайности\n"
            "- НЕ ломай существующие механики\n"
            "- Заменяй reply_text на reply\n"
            "- Убирай Update, Application, filters из импортов\n"
            "- Первая строка ответа — import. Без пояснений, без markdown."
            "- Не оборачивай код в ``` или ```python."
        )
        return self._call(code, system_prompt, temperature=1.0)

    def _call(self, code, system_prompt, temperature):
        import time

        max_code_len = 4000
        if len(code) > max_code_len:
            self.logger.warning(f"Код большой ({len(code)} символов), обрезаю")
            code = code[:3000] + "\n# ... середина пропущена ...\n" + code[-1000:]

        models = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemini-2.0-flash-001:free",
        ]
        last_error = None

        for model in models:
            for attempt in range(2):
                try:
                    chat = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Код:\n\n{code}"},
                        ],
                        temperature=temperature,
                        max_tokens=4000,
                    )
                    result = self._clean(chat.choices[0].message.content)
                    tokens = chat.usage.total_tokens if hasattr(chat, "usage") else "?"
                    self.logger.info(f"LLM ответ ({model}): {len(result)} символов, {tokens} токенов")
                    return result
                except Exception as e:
                    last_error = e
                    error_str = str(e)
                    if "429" in error_str or "rate" in error_str.lower():
                        wait = 60
                        self.logger.warning(f"Рейт-лимит {model}, жду {wait} сек")
                        time.sleep(wait)
                    elif "404" in error_str:
                        self.logger.warning(f"Модель {model} недоступна, пробую следующую")
                        break
                    else:
                        self.logger.warning(f"Ошибка {model}: {error_str[:100]}")
                        time.sleep(10)

        self.logger.error(f"Все модели недоступны. Ошибка: {last_error}")
        raise last_error

    @staticmethod
    def _clean(raw):
        """Очистка вывода LLM."""
        cleaned = raw.strip()

        # Убираем markdown
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        # Убираем строки с ```
        lines = [l for l in cleaned.split("\n") if l.strip() != "```"]

        # Ищем начало кода
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ", "#!", "#!/", "async def ", "def ", "class ", "BOT_TOKEN", "logger")):
                return "\n".join(lines[i:])

        return "\n".join(lines)