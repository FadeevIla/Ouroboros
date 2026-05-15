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
            "Ты — senior Python-разработчик. Исправь баги в коде телеграм-бота: "
            "потерянные await, необработанные исключения, ошибки в API Telegram, "
            "проблемы с типами. НЕ трогай импорты из core.*. "
            "Верни ПОЛНЫЙ исправленный код. Без объяснений, без markdown."
        )
        return self._call(code, system_prompt, temperature=0.2)

    def generate_feature(self, code):
        self.logger.info("LLM: генерация фичи")
        system_prompt = (
            "Ты — разработчик телеграм-ботов. Добавь одну новую команду. "
            "НЕ ломай существующие команды. НЕ добавляй os.system, subprocess, eval, exec. "
            "НЕ трогай импорты core.*. "
            "ВАЖНО: при старте бота (в main или при инициализации) ОБЯЗАТЕЛЬНО сделай рассылку "
            "всем пользователям из core.user_manager о новом обновлении. "
            "Используй core.update_notifier.get_update_description() для получения описания "
            "и core.user_manager.get_all_users() для получения списка chat_id. "
            "Отправь сообщение каждому пользователю через bot.send_message()."
            "Верни ПОЛНЫЙ код с новой фичей. Без объяснений, без markdown."
        )
        return self._call(code, system_prompt, temperature=1.0)

    def _call(self, code, system_prompt, temperature):
        try:
            # Жёстко обрезаем код до 2500 символов, чтобы влезть в лимит 6000 TPM
            # Оставляем: импорты + огрызок кода = ~4000 токенов
            max_code_len = 3000  # было 2500 — даём больше контекста
            if len(code) > max_code_len:
                code = code[:2000] + "\n# ... пропущено ...\n" + code[-1000:]  # больше начала

            chat = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Код bot.py:\n\n{code}"}
                ],
                model="llama-3.1-8b-instant",
                temperature=temperature,
                max_tokens=2500,  # было 1500 — даём больше места для ответа
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