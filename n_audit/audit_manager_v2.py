"""
Полностью переделанный менеджер аудита с реальной диагностикой.
Включает подробное логирование, проверку файлов и реальный анализ.
"""
import os
import json
import threading
import time
from typing import Callable, Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import sys

from n_audit import code_analysis, security, tests_analysis, infrastructure, recommendations


class AuditStatus(Enum):
    """Статусы аудита"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class AuditPhase:
    """Информация о фазе аудита"""
    name: str
    progress: int
    status: str
    message: str


@dataclass
class IssueDetail:
    """Детальная информация об ошибке"""
    type: str  # error, warning, convention, refactor
    file: str
    line: int
    column: int
    message: str
    code: str


@dataclass
class AuditResult:
    """Результат аудита"""
    total_issues: int
    code_issues: int
    security_issues: int
    test_coverage: float
    rating: float
    recommendations: list
    phases: Dict[str, Any]
    issue_details: List[IssueDetail]
    timestamp: str
    project_path: str
    files_analyzed: int
    python_files_count: int
    has_code: bool
    analysis_log: List[str]


class AuditManager:
    """Менеджер аудита с полной диагностикой и логированием"""

    def __init__(self):
        self.status = AuditStatus.IDLE
        self.current_progress = 0
        self.current_phase = None
        self.result: Optional[AuditResult] = None
        self.audit_thread: Optional[threading.Thread] = None
        self.cancel_requested = False

        # Обратные вызовы для GUI
        self.on_progress: Optional[Callable[[int, str], None]] = None
        self.on_phase_update: Optional[Callable[[AuditPhase], None]] = None
        self.on_result: Optional[Callable[[AuditResult], None]] = None  # Новый callback
        self.on_complete: Optional[Callable[[AuditResult], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_log: Optional[Callable[[str], None]] = None  # Логирование

        # Параметры аудита
        self.target_path = "."
        self.exclude_patterns = []
        self.report_level = "full"
        self.export_format = "html"
        self.verbose = True  # Всегда включено для диагностики
        
        # Логирование
        self.analysis_log: List[str] = []

    def set_callbacks(
        self,
        on_progress: Optional[Callable] = None,
        on_phase_update: Optional[Callable] = None,
        on_result: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_log: Optional[Callable] = None,
    ):
        """Установка обратных вызовов для интеграции с GUI"""
        if on_progress:
            self.on_progress = on_progress
        if on_phase_update:
            self.on_phase_update = on_phase_update
        if on_result:
            self.on_result = on_result
        if on_complete:
            self.on_complete = on_complete
        if on_error:
            self.on_error = on_error
        if on_log:
            self.on_log = on_log

    def _log(self, message: str):
        """Логирование с выводом в GUI"""
        self.analysis_log.append(message)
        try:
            print(message, flush=True)
        except UnicodeEncodeError:
            # Fallback для кодировки консоли Windows
            print(message.encode('utf-8', errors='replace').decode('utf-8', errors='replace'), flush=True)
        if self.on_log:
            self.on_log(message)

    def start_audit(self, target_path: str = ".", exclude_patterns: list = None):
        """Запуск аудита"""
        self.target_path = target_path
        self.exclude_patterns = exclude_patterns or []
        
        if self.status == AuditStatus.RUNNING:
            self._log("❌ Аудит уже выполняется")
            if self.on_error:
                self.on_error("Аудит уже выполняется")
            return

        self.cancel_requested = False
        self.status = AuditStatus.RUNNING
        self.current_progress = 0
        self.analysis_log = []
        self.audit_thread = threading.Thread(target=self._run_audit, daemon=True)
        self.audit_thread.start()

    def cancel_audit(self):
        """Запрос на отмену аудита"""
        self.cancel_requested = True
        self.status = AuditStatus.CANCELLED
        self._log("⚠️ Отмена аудита...")

    def _update_progress(self, progress: int, message: str):
        """Обновление прогресса"""
        self.current_progress = min(progress, 100)
        self._log(f"📊 Прогресс: {progress}% - {message}")
        if self.on_progress:
            self.on_progress(self.current_progress, message)

    def _update_phase(self, phase_name: str, phase_progress: int, message: str):
        """Обновление текущей фазы"""
        phase = AuditPhase(
            name=phase_name,
            progress=phase_progress,
            status="running",
            message=message
        )
        self.current_phase = phase
        self._log(f"🔄 Фаза: {phase_name} - {message}")
        if self.on_phase_update:
            self.on_phase_update(phase)

    def _run_audit(self):
        """Основной метод аудита (выполняется в отдельном потоке)"""
        try:
            self._log("=" * 80)
            self._log("🚀 ЗАПУСК АУДИТА")
            self._log("=" * 80)
            
            # Проверка пути
            if not os.path.isdir(self.target_path):
                raise ValueError(f"Неверный путь: {self.target_path}")

            self._log(f"📁 Целевой путь: {self.target_path}")

            # Проверка Python файлов
            py_files = self._find_python_files(self.target_path)
            self._log(f"🐍 Python файлов найдено: {len(py_files)}")
            
            if not py_files:
                self._log("⚠️ ВНИМАНИЕ: Не найдено Python файлов в папке!")
                self._log("Аудит продолжится, но результаты могут быть пусты")
            
            # Подготовка директорий
            results_dir = os.path.join(self.target_path, ".audit_results")
            reports_dir = os.path.join(results_dir, "reports")
            configs_dir = os.path.join(results_dir, "configs")

            os.makedirs(reports_dir, exist_ok=True)
            os.makedirs(configs_dir, exist_ok=True)
            self._log(f"📂 Директория отчётов: {reports_dir}")

            # Создание объекта args
            class Args:
                module = self.target_path
                exclude = self.exclude_patterns
                report_level = "full"
                export_format = "json"
                verbose = True

            args = Args()

            # Фаза 1: Статический анализ кода
            if self.cancel_requested:
                return
            self._update_phase("Статический анализ кода", 10, "Запуск pylint, flake8, radon...")
            self._update_progress(10, "Запуск анализа кода")
            try:
                self._log("🔍 Запуск code_analysis.run()...")
                code_analysis.run(args, reports_dir)
                self._log("✅ code_analysis завершена")
                self._log_files_in_dir(reports_dir, "code analysis")
            except Exception as e:
                self._log(f"⚠️ Ошибка в code_analysis: {e}")
                import traceback
                self._log(traceback.format_exc())
            self._update_progress(25, "Статический анализ завершён")

            # Фаза 2: Проверка безопасности
            if self.cancel_requested:
                return
            self._update_phase("Проверка безопасности", 20, "Запуск bandit, safety...")
            self._update_progress(30, "Запуск проверки безопасности")
            try:
                self._log("🔒 Запуск security.run()...")
                security.run(args, reports_dir)
                self._log("✅ security завершена")
                self._log_files_in_dir(reports_dir, "security")
            except Exception as e:
                self._log(f"⚠️ Ошибка в security: {e}")
                import traceback
                self._log(traceback.format_exc())
            self._update_progress(45, "Проверка безопасности завершена")

            # Фаза 3: Анализ тестов
            if self.cancel_requested:
                return
            self._update_phase("Анализ тестового покрытия", 30, "Запуск pytest, coverage...")
            self._update_progress(50, "Запуск анализа тестов")
            try:
                self._log("🧪 Запуск tests_analysis.run()...")
                tests_analysis.run(args, reports_dir)
                self._log("✅ tests_analysis завершена")
                self._log_files_in_dir(reports_dir, "tests")
            except Exception as e:
                self._log(f"⚠️ Ошибка в tests_analysis: {e}")
                import traceback
                self._log(traceback.format_exc())
            self._update_progress(60, "Анализ тестов завершён")

            # Фаза 4: Анализ инфраструктуры
            if self.cancel_requested:
                return
            self._update_phase("Анализ инфраструктуры", 40, "Запуск проверки зависимостей...")
            self._update_progress(65, "Запуск анализа инфраструктуры")
            try:
                self._log("🏗️ Запуск infrastructure.run()...")
                infrastructure.run(args, reports_dir, configs_dir)
                self._log("✅ infrastructure завершена")
                self._log_files_in_dir(reports_dir, "infrastructure")
            except Exception as e:
                self._log(f"⚠️ Ошибка в infrastructure: {e}")
                import traceback
                self._log(traceback.format_exc())
            self._update_progress(75, "Анализ инфраструктуры завершён")

            # Фаза 5: Генерация рекомендаций
            if self.cancel_requested:
                return
            self._update_phase("Генерация рекомендаций", 50, "Анализ результатов...")
            self._update_progress(85, "Генерация рекомендаций")
            try:
                self._log("💡 Генерация recommendations...")
                recs = recommendations.generate_advices(reports_dir)
                self._log("✅ Рекомендации готовы")
            except Exception as e:
                self._log(f"⚠️ Ошибка в recommendations: {e}")
                recs = "Рекомендации не доступны"
            self._update_progress(90, "Рекомендации готовы")

            # Фаза 6: Формирование итогового отчета
            if self.cancel_requested:
                return
            self._update_phase("Формирование отчёта", 60, "Компиляция данных...")
            self._update_progress(95, "Создание финального отчета")

            # Загрузка результатов
            self._log("📋 Загрузка результатов...")
            result = self._load_results(reports_dir, recs, len(py_files))

            self._update_progress(100, "Аудит завершён успешно!")
            self.status = AuditStatus.COMPLETED
            self.result = result

            self._log("=" * 80)
            self._log(f"✅ АУДИТ ЗАВЕРШЕН")
            self._log(f"📊 Рейтинг: {result.rating}/10")
            self._log(f"🐛 Ошибок кода: {result.code_issues}")
            self._log(f"🔓 Уязвимостей: {result.security_issues}")
            self._log(f"🧪 Покрытие тестами: {result.test_coverage}%")
            self._log("=" * 80)

            # Вызываем оба callback для совместимости
            if self.on_result:
                self.on_result(result)
            if self.on_complete:
                self.on_complete(result)

        except Exception as e:
            self.status = AuditStatus.ERROR
            error_msg = f"❌ Ошибка при выполнении аудита: {str(e)}"
            self._log(error_msg)
            import traceback
            self._log(traceback.format_exc())
            if self.on_error:
                self.on_error(error_msg)

    def _find_python_files(self, directory: str) -> List[str]:
        """Поиск всех Python файлов в директории"""
        py_files = []
        for root, dirs, files in os.walk(directory):
            # Пропускаем служебные директории
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        return py_files

    def _log_files_in_dir(self, directory: str, phase: str):
        """Логирование файлов в директории после фазы"""
        try:
            files = os.listdir(directory)
            if files:
                self._log(f"  📁 Файлы в {phase}:")
                for f in files:
                    fpath = os.path.join(directory, f)
                    size = os.path.getsize(fpath)
                    self._log(f"    - {f} ({size} байт)")
            else:
                self._log(f"  ⚠️ Нет файлов в {phase}")
        except:
            pass

    def _load_results(self, reports_dir: str, recommendations_text: str, py_files_count: int) -> AuditResult:
        """Загрузка и парсинг результатов с полной диагностикой"""
        
        self._log(f"🔎 Парсинг результатов из: {reports_dir}")
        
        phases = {}
        code_issues = 0
        security_issues = 0
        test_coverage = 0.0
        issue_details: List[IssueDetail] = []
        files_analyzed = 0
        has_code = py_files_count > 0

        # ===== АНАЛИЗ КОДА =====
        self._log("\n📋 Анализ результатов code_analysis:")
        try:
            # Ищем результаты pylint
            for fname in ["pylint_full.json", "pylint_results.json", "code_quality.json"]:
                fpath = os.path.join(reports_dir, fname)
                if os.path.exists(fpath):
                    self._log(f"  📄 Найден файл: {fname}")
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            
                        if isinstance(data, list):
                            self._log(f"    Формат: список из {len(data)} элементов")
                            for issue in data:
                                if isinstance(issue, dict):
                                    msg_type = issue.get("type", "error")
                                    if msg_type in ["error", "fatal"]:
                                        code_issues += 1
                                        issue_details.append(IssueDetail(
                                            type=msg_type,
                                            file=issue.get("path", "unknown"),
                                            line=issue.get("line", 0),
                                            column=issue.get("column", 0),
                                            message=issue.get("message", ""),
                                            code=issue.get("symbol", "")
                                        ))
                                    elif msg_type in ["warning", "convention", "refactor"]:
                                        code_issues += 0.5  # Считаем предупреждения со скидкой
                        
                        elif isinstance(data, dict):
                            self._log(f"    Формат: словарь с ключами {list(data.keys())}")
                            if "results" in data:
                                code_issues += len(data["results"])
                            if "errors" in data:
                                code_issues += len(data["errors"])
                        
                        self._log(f"    ✅ Обработано, найдено ошибок: {int(code_issues)}")
                        break
                    except Exception as e:
                        self._log(f"    ❌ Ошибка парсинга: {e}")
                        continue

            # Ищем результаты flake8
            for fname in ["flake8_results.json", "flake8_report.json"]:
                fpath = os.path.join(reports_dir, fname)
                if os.path.exists(fpath):
                    self._log(f"  📄 Найден файл: {fname}")
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        flake8_count = len(data) if isinstance(data, list) else data.get("total", 0)
                        code_issues += flake8_count * 0.3  # Считаем менее критично
                        self._log(f"    ✅ Найдено проблем: {flake8_count}")
                    except Exception as e:
                        self._log(f"    ❌ Ошибка парсинга: {e}")

            # Ищем результаты mypy
            for fname in ["mypy_results.json"]:
                fpath = os.path.join(reports_dir, fname)
                if os.path.exists(fpath):
                    self._log(f"  📄 Найден файл: {fname}")
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        mypy_count = len(data) if isinstance(data, list) else 0
                        code_issues += mypy_count * 0.5
                        self._log(f"    ✅ Найдено ошибок типизации: {mypy_count}")
                    except Exception as e:
                        self._log(f"    ❌ Ошибка парсинга: {e}")

            phases["code_analysis"] = {"issues": int(code_issues)}
            self._log(f"  📊 Итого ошибок кода: {int(code_issues)}")

        except Exception as e:
            self._log(f"  ❌ Ошибка загрузки code_analysis: {e}")

        # ===== АНАЛИЗ БЕЗОПАСНОСТИ =====
        self._log("\n🔒 Анализ результатов security:")
        try:
            for fname in ["security_issues.json", "bandit_results.json", "vulnerabilities.json"]:
                fpath = os.path.join(reports_dir, fname)
                if os.path.exists(fpath):
                    self._log(f"  📄 Найден файл: {fname}")
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        
                        if isinstance(data, dict):
                            if "results" in data:
                                security_issues = len(data["results"])
                            elif "errors" in data:
                                security_issues = len(data["errors"])
                            elif "issues" in data:
                                security_issues = data["issues"]
                        elif isinstance(data, list):
                            security_issues = len(data)
                        
                        self._log(f"    ✅ Найдено уязвимостей: {security_issues}")
                        break
                    except Exception as e:
                        self._log(f"    ❌ Ошибка парсинга: {e}")

            phases["security"] = {"issues": security_issues}
            self._log(f"  📊 Итого уязвимостей: {security_issues}")

        except Exception as e:
            self._log(f"  ❌ Ошибка загрузки security: {e}")

        # ===== ТЕСТОВОЕ ПОКРЫТИЕ =====
        self._log("\n🧪 Анализ результатов tests:")
        try:
            fpath = os.path.join(reports_dir, "coverage.json")
            if os.path.exists(fpath):
                self._log(f"  📄 Найден файл: coverage.json")
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict):
                        if "totals" in data and "percent_covered" in data["totals"]:
                            test_coverage = data["totals"]["percent_covered"]
                        elif "coverage" in data:
                            test_coverage = data["coverage"]
                    
                    self._log(f"    ✅ Покрытие тестами: {test_coverage}%")
                except Exception as e:
                    self._log(f"    ❌ Ошибка парсинга: {e}")
            else:
                self._log(f"  ⚠️ Файл coverage.json не найден")

            phases["tests"] = {"coverage": test_coverage}

        except Exception as e:
            self._log(f"  ❌ Ошибка загрузки tests: {e}")

        # ===== РАСЧЕТ РЕЙТИНГА =====
        self._log("\n📊 Расчёт рейтинга:")
        rating = self._calculate_rating(code_issues, security_issues, test_coverage, has_code)
        self._log(f"  Ошибок кода: {int(code_issues)} × 0.3 = -{int(code_issues)*0.3}")
        self._log(f"  Уязвимостей: {security_issues} × 0.8 = -{security_issues*0.8}")
        self._log(f"  Покрытие: {test_coverage}%")
        self._log(f"  📈 Итоговый рейтинг: {rating}/10")

        # Преобразование рекомендаций
        if isinstance(recommendations_text, str):
            recommendations_list = [
                rec.strip() for rec in recommendations_text.split("\n")
                if rec.strip() and not rec.startswith("#")
            ]
        else:
            recommendations_list = []

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return AuditResult(
            total_issues=int(code_issues) + security_issues,
            code_issues=int(code_issues),
            security_issues=security_issues,
            test_coverage=test_coverage,
            rating=rating,
            recommendations=recommendations_list[:10],  # Первые 10
            phases=phases,
            issue_details=issue_details,
            timestamp=timestamp,
            project_path=self.target_path,
            files_analyzed=py_files_count,
            python_files_count=py_files_count,
            has_code=has_code,
            analysis_log=self.analysis_log
        )

    @staticmethod
    def _calculate_rating(code_issues: float, security_issues: int, test_coverage: float, has_code: bool) -> float:
        """Расчет рейтинга с учётом наличия кода"""
        
        # Если нет кода - низкая оценка
        if not has_code:
            return 2.0
        
        base_rating = 10.0
        
        # Штраф за ошибки кода (0.3 за ошибку)
        code_deduction = min(0.3 * code_issues, 5.0)  # Максимум -5
        
        # Штраф за уязвимости (0.8 за ошибку - более критично)
        security_deduction = min(0.8 * security_issues, 4.0)  # Максимум -4
        
        # Бонус за тестовое покрытие
        coverage_bonus = 0
        if test_coverage >= 80:
            coverage_bonus = 1.0
        elif test_coverage >= 60:
            coverage_bonus = 0.5
        elif test_coverage == 0:
            coverage_bonus = -1.0  # Штраф за отсутствие тестов
        
        # Итоговый расчет
        rating = base_rating - code_deduction - security_deduction + coverage_bonus
        rating = max(1.0, min(10.0, rating))  # От 1 до 10
        
        return round(rating, 1)

    def get_status(self) -> Dict[str, Any]:
        """Получить текущий статус аудита"""
        return {
            "status": self.status.value,
            "progress": self.current_progress,
            "phase": self.current_phase.name if self.current_phase else None,
            "result": asdict(self.result) if self.result else None
        }
