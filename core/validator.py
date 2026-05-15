# core/validator.py
"""Валидация Python-кода перед пушем."""
import os
import tempfile
from groq import Groq


class Validator:
    def __init__(self, groq_client, logger, notifier=None):
        self.groq_client = groq_client
        self.logger = logger
        self.notifier = notifier

    def validate_syntax(self, code):
        try:
            compile(code, "<generated>", "exec")
            return True, None
        except SyntaxError as e:
            return False, f"Синтаксическая ошибка: {e.msg} (строка {e.lineno})"

    def validate_imports(self, code):
        required = ["telegram", "Telegram", "Bot", "Application"]
        # Проверяем, что код похож на телеграм-бота
        has_bot_framework = any(kw in code for kw in required)
        if not has_bot_framework:
            return False, "Код не похож на телеграм-бота (нет импортов telegram)"

        dangerous = ["os.system", "subprocess.call", "eval(", "exec("]
        for danger in dangerous:
            if danger in code:
                return False, f"Обнаружен опасный вызов: {danger}"

        return True, None

    def validate_pyflakes(self, code):
        try:
            import pyflakes.api
            import pyflakes.reporter

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                tmp.write(code)
                tmp.flush()
                tmp_path = tmp.name

            errors = []
            reporter = pyflakes.reporter.Reporter(
                lambda msg: errors.append(str(msg)),
                lambda msg: None
            )
            pyflakes.api.checkPath(tmp_path, reporter)
            os.unlink(tmp_path)

            if errors:
                return False, f"Pyflakes: {'; '.join(errors[:3])}"
            return True, None
        except ImportError:
            return True, None
        except Exception as e:
            return False, f"Pyflakes error: {e}"

    def full_validation(self, code, max_retries=3):
        self.logger.info(f"Валидация (макс. попыток: {max_retries})")

        for attempt in range(max_retries):
            self.logger.info(f"Попытка {attempt + 1}/{max_retries}")

            syntax_ok, syntax_err = self.validate_syntax(code)
            if not syntax_ok:
                self.logger.warning(f"[{attempt + 1}] {syntax_err}")
                if attempt < max_retries - 1:
                    code = self._llm_fix(code, syntax_err, "syntax")
                    continue
                return False, code, syntax_err

            imports_ok, imports_err = self.validate_imports(code)
            if not imports_ok:
                self.logger.warning(f"[{attempt + 1}] {imports_err}")
                if attempt < max_retries - 1:
                    code = self._llm_fix(code, imports_err, "imports")
                    continue
                return False, code, imports_err

            pyflakes_ok, pyflakes_err = self.validate_pyflakes(code)
            if not pyflakes_ok:
                self.logger.warning(f"[{attempt + 1}] {pyflakes_err}")
                # Не блокируем, но предупреждаем

            self.logger.info("Валидация пройдена")
            return True, code, None

        return False, code, "Исчерпаны попытки"

    def _llm_fix(self, code, error, fix_type):
        prompts = {
            "syntax": ("Исправь ТОЛЬКО синтаксическую ошибку. Верни полный код без markdown.", 0.1),
            "imports": (
                "Исправь проблемы с импортами. Добавь недостающие, убери опасные. Верни полный код без markdown.", 0.1),
        }
        prompt, temp = prompts.get(fix_type, prompts["syntax"])

        chat = self.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Ошибка: {error}\n\nКод:\n{code}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=temp,
            max_tokens=15000,
        )
        return self._clean_output(chat.choices[0].message.content)

    @staticmethod
    def _clean_output(raw):
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        return cleaned