# core/llm_interface.py
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
        system_prompt = (
            "Ты — Python-разработчик. Исправь ВСЕ баги в коде телеграм-бота. "
            "Верни ПОЛНЫЙ код. Без markdown."
        )
        return self._call(code, system_prompt, temperature=0.2)

    def generate_feature(self, code):
        self.logger.info("LLM: генерация фичи")
        system_prompt = (
            "Ты — разработчик телеграм-ботов. Добавь ОДНУ новую команду (/joke, /fact, /quote, /weather, /poll, /stats, /remind, /whatsnew). "
            "Сохрани все существующие команды. Верни ПОЛНЫЙ код. Без markdown."
        )
        return self._call(code, system_prompt, temperature=1.0)

    def _call(self, code, system_prompt, temperature):
        try:
            # Жёстко обрезаем код до 2500 символов, чтобы влезть в лимит 6000 TPM
            # Оставляем: импорты + огрызок кода = ~4000 токенов
            max_code_len = 3500
            if len(code) > max_code_len:
                # Берём первые 2500 + последние 1000
                code = code[:2500] + "\n# ... код сокращён ...\n" + code[-1000:]

            chat = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Код bot.py:\n\n{code}"}
                ],
                model="llama-3.1-8b-instant",
                temperature=temperature,
                max_tokens=3000,  # больше места для ответа
            )

            result = self._clean(chat.choices[0].message.content)
            tokens = chat.usage.total_tokens if hasattr(chat, "usage") else "?"
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