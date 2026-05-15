# core/llm_interface.py — ИСПРАВЛЕННАЯ ВЕРСИЯ
"""Интерфейс для работы с Groq LLM."""
from groq import Groq


class LLMInterface:
    def __init__(self, api_key, logger, notifier=None):
        self.logger = logger
        self.notifier = notifier
        self.logger.info("Инициализация Groq")
        self.client = Groq(api_key=api_key)
        self.logger.info("Groq готов")

    def analyze_bugs(self, code):
        self.logger.info("LLM: поиск багов")
        system_prompt = """Ты — senior Python-разработчик. Исправь баги в коде телеграм-бота: потерянные await, необработанные исключения, ошибки в API Telegram, проблемы с типами. НЕ трогай импорты из core.*. Верни ПОЛНЫЙ исправленный код. Без объяснений, без markdown."""

        return self._call(code, system_prompt, temperature=0.2)

    def generate_feature(self, code):
        self.logger.info("LLM: генерация фичи")
        system_prompt = """Ты — разработчик телеграм-ботов. Добавь одну новую команду: /joke, /fact, /quote, /weather, /poll, /stats или /remind. НЕ ломай существующие команды. НЕ добавляй os.system, subprocess, eval, exec. НЕ трогай импорты core.*. Верни ПОЛНЫЙ код с новой фичей. Без объяснений, без markdown."""

        return self._call(code, system_prompt, temperature=1.0)

    def _call(self, code, system_prompt, temperature):
        try:
            # Если код слишком большой — обрезаем до 4000 символов
            if len(code) > 4000:
                self.logger.warning(f"Код слишком большой ({len(code)} символов), обрезаю до 4000")
                code = code[:4000] + "\n# ... (код обрезан для лимита токенов)"

            chat = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Код bot.py:\n\n{code}"}
                ],
                model="llama-3.2-3b-preview",  # Бесплатная, лимит 8000 TPM
                temperature=temperature,
                max_tokens=4000,  # Ограничиваем ответ
            )

            result = self._clean(chat.choices[0].message.content)
            tokens = chat.usage.total_tokens if hasattr(chat, 'usage') else '?'
            self.logger.info(f"LLM ответ: {len(result)} символов, {tokens} токенов")
            return result
        except Exception as e:
            self.logger.error(f"LLM error: {e}")
            if self.notifier:
                self.notifier.send(f"❌ Ошибка LLM: {str(e)[:200]}", "error")
            raise

    @staticmethod
    def _clean(raw):
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        return cleaned