# self_fixing_bot.py — ОРКЕСТРАТОР (НЕ трогается LLM)
"""
Дарвин — бот, который сам себя улучшает.
Оркестратор цикла самосовершенствования.
"""
import sys
import time
import random
import traceback
from datetime import datetime, timezone
from pathlib import Path

# 🔧 Автозагрузка .env файла
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ .env файл загружен")
except ImportError:
    print("ℹ️  python-dotenv не установлен, .env не загружается")
    print("   Установи: pip install python-dotenv")

# Добавляем корень в path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import load_config
from core.logger import setup_logging
from core.notifier import Notifier
from core.memory import Memory
from core.validator import Validator
from core.github_ops import GitHubOps
from core.llm_interface import LLMInterface


class DarwinOrchestrator:
    """Оркестратор цикла самосовершенствования."""

    def __init__(self):
        # Загружаем конфиг
        self.config = load_config()

        # Настраиваем логирование
        self.logger, self.event_logger = setup_logging()
        self.logger.info("=" * 50)
        self.logger.info("ДАРВИН: Оркестратор инициализируется")
        self.logger.info("=" * 50)

        # Уведомления
        self.notifier = Notifier(
            self.config["TG_BOT_TOKEN"],
            self.config["TG_CHAT_ID"],
            self.logger
        )

        # Память
        self.memory = Memory(self.config["MEMORY_FILE"], self.logger)

        # LLM интерфейс
        self.llm = LLMInterface(
            self.config["GROQ_API_KEY"],
            self.logger,
            self.notifier
        )

        # Валидатор
        self.validator = Validator(
            self.llm.client,
            self.logger,
            self.notifier
        )

        # GitHub операции
        self.github = GitHubOps(
            self.config["GITHUB_TOKEN"],
            self.config["REPO_NAME"],
            self.config["BOT_FILE_PATH"],
            self.logger,
            self.notifier
        )

        self.logger.info("✅ Оркестратор готов")
        self.notifier.send(
            "🤖 <b>Дарвин запущен</b>\n"
            f"📁 Репозиторий: <code>{self.config['REPO_NAME']}</code>\n"
            f"📄 Целевой файл: <code>{self.config['BOT_FILE_PATH']}</code>\n"
            f"🧠 Память: {len(self.memory.data['features'])} фич",
            "heartbeat"
        )

    def run_cycle(self):
        """Один полный цикл самосовершенствования."""
        cycle_start = datetime.now(timezone.utc)
        self.logger.info("#" * 60)
        self.logger.info(f"ЦИКЛ НАЧАТ: {cycle_start.isoformat()}")
        self.logger.info("#" * 60)

        self.notifier.send(
            f"🔄 Цикл запущен\n"
            f"⏱️ {cycle_start.strftime('%H:%M:%S UTC')}\n"
            f"🧠 Память: {len(self.memory.data['features'])} фич",
            "heartbeat"
        )

        stats = {"bugs_fixed": False, "feature_added": False, "errors": []}

        # --- Шаг 1: Загрузка кода ---
        try:
            self.notifier.send("📥 Загрузка кода из репозитория...", "info")
            code, sha = self.github.get_code()
        except Exception as e:
            self.logger.critical(f"Ошибка загрузки: {e}")
            self.notifier.send(f"💥 Критическая ошибка загрузки: {str(e)[:200]}", "error")
            return False

        # --- Шаг 2: Поиск и исправление багов ---
        try:
            self.notifier.send("🔍 Поиск багов через LLM...", "info")
            fixed_code = self.llm.analyze_bugs(code)

            if fixed_code != code:
                self.logger.info(f"Найдены изменения: {abs(len(fixed_code) - len(code))} байт")
                self.notifier.send(
                    f"🐛 Найдены баги\nРазница: {abs(len(fixed_code) - len(code))} байт",
                    "fix"
                )

                is_dup, reason = self.memory.is_duplicate(fixed_code)
                if is_dup:
                    self.logger.info(f"Пропуск: дубликат ({reason})")
                    self.notifier.send(f"⏭️ Фикс пропущен: {reason}", "warning")
                else:
                    valid, validated_code, err = self.validator.full_validation(fixed_code)
                    if valid:
                        commit_msg = "🤖 Auto-fix: нейросеть исправила баги"
                        commit_sha = self.github.push(validated_code, sha, commit_msg)
                        self.memory.add_feature(validated_code, "fix")
                        self.memory.add_commit(commit_sha, "Auto-fix")
                        code, sha = validated_code, commit_sha
                        stats["bugs_fixed"] = True
                    else:
                        stats["errors"].append(f"Валидация фикса: {err}")
            else:
                self.logger.info("Багов не найдено")
                self.notifier.send("✅ Код чист, багов нет", "success")
        except Exception as e:
            self.logger.error(f"Ошибка этапа фикса: {e}")
            stats["errors"].append(f"Фикс: {e}")

        # --- Шаг 3: Генерация новой фичи ---
        try:
            self.notifier.send("💡 Генерация новой фичи...", "info")

            if random.random() > 0.8:
                self.logger.info("Пропуск этапа фич (отдых)")
                self.notifier.send("😴 Бот решил отдохнуть, фичи пропущены", "info")
            else:
                new_code = self.llm.generate_feature(code)

                if new_code != code:
                    self.logger.info(f"Фича сгенерирована: разница {abs(len(new_code) - len(code))} байт")
                    self.notifier.send(
                        f"✨ Новая фича готова\nРазница: {abs(len(new_code) - len(code))} байт",
                        "feature"
                    )

                    is_dup, reason = self.memory.is_duplicate(new_code)
                    if is_dup:
                        self.logger.info(f"Дубликат фичи: {reason}")
                        self.notifier.send(f"⏭️ Фича пропущена: {reason}", "warning")
                    else:
                        valid, validated_code, err = self.validator.full_validation(new_code)
                        if valid:
                            commit_msg = "🤖 Auto-feature: нейросеть добавила новую функцию"
                            commit_sha = self.github.push(validated_code, sha, commit_msg)
                            self.memory.add_feature(validated_code, "feature")
                            self.memory.add_commit(commit_sha, "Auto-feature")
                            stats["feature_added"] = True
                        else:
                            stats["errors"].append(f"Валидация фичи: {err}")
                else:
                    self.logger.info("LLM не предложила новой фичи")
                    self.notifier.send("🤔 Нейросеть не придумала новую фичу", "info")
        except Exception as e:
            self.logger.error(f"Ошибка этапа фичи: {e}")
            stats["errors"].append(f"Фича: {e}")

        # --- Итоги ---
        duration = (datetime.now(timezone.utc) - cycle_start).total_seconds()
        self.logger.info("=" * 60)
        self.logger.info(f"ЦИКЛ ЗАВЕРШЁН: {duration:.1f} сек")
        self.logger.info(
            f"Баги: {stats['bugs_fixed']} | Фичи: {stats['feature_added']} | Ошибки: {len(stats['errors'])}")
        self.logger.info("=" * 60)

        summary = [
            f"⏱️ Длительность: {duration:.1f} сек",
            f"🐛 Баги: {'исправлены' if stats['bugs_fixed'] else 'нет'}",
            f"✨ Фичи: {'добавлены' if stats['feature_added'] else 'нет'}",
        ]
        if stats["errors"]:
            summary.append(f"⚠️ Ошибок: {len(stats['errors'])}")

        level = "success" if not stats["errors"] else "warning"
        self.notifier.send("\n".join(summary), level)

        return len(stats["errors"]) == 0

    def start(self):
        """Запуск бесконечного цикла."""
        interval = self.config["CYCLE_INTERVAL"]
        cycle = 0

        # Проверка подключений
        try:
            self.github.get_code()
            self.logger.info("✅ Все подключения проверены")
        except Exception as e:
            self.logger.critical(f"Ошибка подключения: {e}")
            self.notifier.send(f"💥 Ошибка запуска: {str(e)[:200]}", "error")
            sys.exit(1)

        try:
            while True:
                cycle += 1
                self.logger.info(f"\n{'#' * 60}\n### ЦИКЛ #{cycle}\n{'#' * 60}")

                try:
                    self.run_cycle()
                except Exception as e:
                    self.logger.critical(f"Ошибка цикла #{cycle}: {e}")
                    self.logger.critical(traceback.format_exc())
                    self.notifier.send(f"💥 Ошибка цикла #{cycle}: {str(e)[:200]}", "error")

                self.logger.info(f"Ожидание {interval} сек...")
                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info("Остановлен пользователем")
            self.notifier.send("🛑 Дарвин остановлен вручную", "info")


if __name__ == "__main__":
    orchestrator = DarwinOrchestrator()
    orchestrator.start()