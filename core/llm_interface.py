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
            "Ты — senior Python-разработчик. Проанализируй код телеграм-бота "
            "и исправь ВСЕ баги. Обрати внимание на: потерянные await/asyncio, "
            "необработанные исключения, ошибки в логике работы с API Telegram, "
            "проблемы с типами данных, отсутствующие импорты.\n"
            "НЕ трогай импорты из core.*.\n"
            "Верни ПОЛНЫЙ исправленный код. Без объяснений, без markdown."
        )
        return self._call(code, system_prompt, temperature=0.2)

    def generate_feature(self, code):
        self.logger.info("LLM: генерация фичи")
        system_prompt = (
            "Ты — креативный разработчик телеграм-ботов. Добавь в код ОДНУ новую "
            "полезную команду или фичу. Идеи: /joke, /fact, /quote, /weather, "
            "/poll, /stats, /remind, /whatsnew.\n"
            "ПРАВИЛА:\n"
            "1. НЕ ломай существующие команды и функционал\n"
            "2. НЕ добавляй: os.system, subprocess, eval, exec\n"
            "3. НЕ меняй импорты из core.* модулей\n"
            "4. НЕ удаляй существующие импорты\n"
            "5. Добавляй ТОЛЬКО новые команды/фичи\n\n"
            "Верни ПОЛНЫЙ код bot.py с новой фичей. Без объяснений, без markdown."
        )
        return self._call(code, system_prompt, temperature=1.0)

    def _call(self, code, system_prompt, temperature):
        try:
            # DeepSeek R1 бесплатная принимает до 8192 токенов
            # Режем код до 4000 символов (~5000 токенов) + промпт = укладываемся
            max_code_len = 4000
            if len(code) > max_code_len:
                self.logger.warning(
                    f"Код большой ({len(code)} символов), обрезаю до {max_code_len}"
                )
                code = code[:3000] + "\n# ... середина пропущена ...\n" + code[-1000:]

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
            tokens = chat.usage.total_tokens if hasattr(chat, "usage") else "?"
            self.logger.info(
                f"LLM ответ: {len(result)} символов, {tokens} токенов"
            )
            return result
        except Exception as e:
            self.logger.error(f"LLM error: {e}")
            if self.notifier:
                self.notifier.send(f"❌ Ошибка LLM: {str(e)[:200]}", "error")
            raise

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