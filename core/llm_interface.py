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
        system_prompt = """Ты — senior Python-разработчик. Проанализируй код телеграм-бота и исправь ВСЕ баги.
Обрати внимание на:
- потерянные await/asyncio
- необработанные исключения
- ошибки в логике работы с API Telegram
- проблемы с типами данных
- отсутствующие импорты

ВАЖНО: ты редактируешь ТОЛЬКО файл bot.py. 
НЕ трогай следующие модули (их импорты в начале файла):
- from core.config import load_config
- from core.logger import setup_logging
- from core.notifier import Notifier
- from core.memory import Memory
- from core.validator import Validator
- from core.github_ops import GitHubOps
- from core.llm_interface import LLMInterface

Верни ПОЛНЫЙ исправленный код bot.py. Без объяснений, без markdown."""

        return self._call(code, system_prompt, temperature=0.2)

    def generate_feature(self, code):
        self.logger.info("LLM: генерация фичи")
        system_prompt = """Ты — креативный разработчик телеграм-ботов. Добавь в код одну новую полезную команду или фичу.
Идеи для фич:
- /joke — случайная шутка
- /fact — интересный факт
- /quote — случайная цитата
- /weather город — прогноз погоды
- /poll вопрос — создание опроса
- /stats — статистика чата
- /remind время текст — напоминание
- Ежедневная утренняя сводка
- Приветствие новых пользователей
- Команда с эмодзи-реакциями

ПРАВИЛА:
1. НЕ ломай существующие команды и функционал
2. НЕ добавляй: os.system, subprocess, eval, exec
3. НЕ меняй импорты из core.* модулей
4. НЕ удаляй существующие импорты
5. Добавляй ТОЛЬКО новые команды/фичи, не переписывай существующее

Верни ПОЛНЫЙ код bot.py с новой фичей. Без объяснений, без markdown."""

        return self._call(code, system_prompt, temperature=1.0)

    def _call(self, code, system_prompt, temperature):
        try:
            chat = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Вот текущий код bot.py:\n\n{code}"}
                ],
                model="llama-3.1-8b-instant",
                temperature=temperature,
                max_tokens=15000,
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