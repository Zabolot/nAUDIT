"""
Менеджер аудита с поддержкой асинхронных операций и обратных вызовов.
Используется для интеграции с GUI приложением.
"""
import os
import json
import threading
import time
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

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
class AuditResult:
    """Результат аудита"""
    total_issues: int
    code_issues: int
    security_issues: int
    test_coverage: float
    rating: float
    recommendations: list
    phases: Dict[str, Any]


class AuditManager:
    """Менеджер аудита с поддержкой GUI интеграции"""

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
        self.on_complete: Optional[Callable[[AuditResult], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

        # Параметры аудита
        self.target_path = "."
        self.exclude_patterns = []
        self.report_level = "full"
        self.export_format = "html"
        self.verbose = False

    def set_callbacks(
        self,
        on_progress: Optional[Callable] = None,
        on_phase_update: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ):
        """Установка обратных вызовов для интеграции с GUI"""
        if on_progress:
            self.on_progress = on_progress
        if on_phase_update:
            self.on_phase_update = on_phase_update
        if on_complete:
            self.on_complete = on_complete
        if on_error:
            self.on_error = on_error

    def configure(
        self,
        target_path: str,
        exclude_patterns: list = None,
        report_level: str = "full",
        export_format: str = "html",
        verbose: bool = False,
    ):
        """Конфигурация параметров аудита"""
        self.target_path = target_path
        self.exclude_patterns = exclude_patterns or []
        self.report_level = report_level
        self.export_format = export_format
        self.verbose = verbose

    def start_audit_async(self):
        """Запуск аудита в отдельном потоке"""
        if self.status == AuditStatus.RUNNING:
            if self.on_error:
                self.on_error("Аудит уже выполняется")
            return

        self.cancel_requested = False
        self.status = AuditStatus.RUNNING
        self.current_progress = 0
        self.audit_thread = threading.Thread(target=self._run_audit, daemon=True)
        self.audit_thread.start()

    def cancel_audit(self):
        """Запрос на отмену аудита"""
        self.cancel_requested = True
        self.status = AuditStatus.CANCELLED

    def _update_progress(self, progress: int, message: str):
        """Обновление прогресса"""
        self.current_progress = min(progress, 100)
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
        if self.on_phase_update:
            self.on_phase_update(phase)

    def _run_audit(self):
        """Основной метод аудита (выполняется в отдельном потоке)"""
        try:
            # Проверка пути
            if not os.path.isdir(self.target_path):
                raise ValueError(f"Неверный путь: {self.target_path}")

            # Подготовка директорий
            results_dir = os.path.join(self.target_path, ".audit_results")
            reports_dir = os.path.join(results_dir, "reports")
            configs_dir = os.path.join(results_dir, "configs")

            os.makedirs(reports_dir, exist_ok=True)
            os.makedirs(configs_dir, exist_ok=True)

            # Создание объекта args для совместимости
            class Args:
                module = self.target_path
                exclude = self.exclude_patterns
                report_level = self.report_level
                export_format = self.export_format
                verbose = self.verbose

            args = Args()

            # Фаза 1: Статический анализ кода
            if self.cancel_requested:
                return
            self._update_phase("Статический анализ кода", 0, "Сканирование Python файлов...")
            self._update_progress(5, "Запуск анализа кода")
            try:
                code_analysis.run(args, reports_dir)
            except Exception as e:
                if self.verbose:
                    print(f"Ошибка в code_analysis: {e}")
            self._update_progress(20, "Статический анализ завершён")

            # Фаза 2: Проверка безопасности
            if self.cancel_requested:
                return
            self._update_phase("Проверка безопасности", 0, "Сканирование уязвимостей...")
            self._update_progress(25, "Запуск проверки безопасности")
            try:
                security.run(args, reports_dir)
            except Exception as e:
                if self.verbose:
                    print(f"Ошибка в security: {e}")
            self._update_progress(40, "Проверка безопасности завершена")

            # Фаза 3: Анализ тестов
            if self.cancel_requested:
                return
            self._update_phase("Анализ тестового покрытия", 0, "Поиск тестов...")
            self._update_progress(45, "Запуск анализа тестов")
            try:
                tests_analysis.run(args, reports_dir)
            except Exception as e:
                if self.verbose:
                    print(f"Ошибка в tests_analysis: {e}")
            self._update_progress(60, "Анализ тестов завершён")

            # Фаза 4: Анализ инфраструктуры
            if self.cancel_requested:
                return
            self._update_phase("Анализ инфраструктуры", 0, "Проверка зависимостей...")
            self._update_progress(65, "Запуск анализа инфраструктуры")
            try:
                infrastructure.run(args, reports_dir, configs_dir)
            except Exception as e:
                if self.verbose:
                    print(f"Ошибка в infrastructure: {e}")
            self._update_progress(80, "Анализ инфраструктуры завершён")

            # Фаза 5: Генерация рекомендаций
            if self.cancel_requested:
                return
            self._update_phase("Генерация рекомендаций", 0, "Анализ результатов...")
            self._update_progress(85, "Генерация рекомендаций")
            try:
                recs = recommendations.generate_advices(reports_dir)
            except Exception as e:
                if self.verbose:
                    print(f"Ошибка в recommendations: {e}")
                recs = "Рекомендации не доступны"
            self._update_progress(90, "Рекомендации готовы")

            # Фаза 6: Формирование итогового отчета
            if self.cancel_requested:
                return
            self._update_phase("Формирование отчёта", 0, "Компиляция данных...")
            self._update_progress(95, "Создание финального отчета")

            # Загрузка результатов
            result = self._load_results(reports_dir, recs)

            self._update_progress(100, "Аудит завершён успешно!")
            self.status = AuditStatus.COMPLETED
            self.result = result

            if self.on_complete:
                self.on_complete(result)

        except Exception as e:
            self.status = AuditStatus.ERROR
            error_msg = f"Ошибка при выполнении аудита: {str(e)}"
            if self.on_error:
                self.on_error(error_msg)
            if self.verbose:
                import traceback
                print(traceback.format_exc())

    def _load_results(self, reports_dir: str, recommendations_text: str) -> AuditResult:
        """Загрузка результатов аудита с расширенной диагностикой"""
        phases = {}
        code_issues = 0
        security_issues = 0
        test_coverage = 0.0

        # Чтение результатов анализа кода (Radon, Pylint и т.д.)
        try:
            # Pylint результаты
            pylint_files = [
                os.path.join(reports_dir, "pylint_full.json"),
                os.path.join(reports_dir, "pylint_results.json"),
                os.path.join(reports_dir, "code_quality.json")
            ]
            
            for pylint_file in pylint_files:
                if os.path.exists(pylint_file):
                    try:
                        with open(pylint_file, "r", encoding="utf-8") as f:
                            pylint_data = json.load(f)
                            if isinstance(pylint_data, list):
                                # Считаем только реальные ошибки и предупреждения
                                code_issues += len([
                                    x for x in pylint_data 
                                    if x.get("type") in ["error", "fatal", "convention", "refactor", "warning"]
                                ])
                            elif isinstance(pylint_data, dict):
                                # Если формат словаря
                                if "errors" in pylint_data:
                                    code_issues += len(pylint_data["errors"])
                                if "issues" in pylint_data:
                                    code_issues += pylint_data["issues"]
                        break
                    except:
                        continue
            
            # Radon результаты (сложность кода)
            radon_file = os.path.join(reports_dir, "complexity.txt")
            if os.path.exists(radon_file):
                try:
                    with open(radon_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Подсчет функций с высокой сложностью
                        complex_functions = content.count("C (10-11)")
                        complex_functions += content.count("C (12-13)")
                        code_issues += complex_functions
                except:
                    pass
            
            phases["code_analysis"] = {"issues": code_issues}
        except Exception as e:
            if self.verbose:
                print(f"Ошибка при загрузке результатов анализа кода: {e}")

        # Чтение результатов проверки безопасности (Bandit)
        try:
            security_files = [
                os.path.join(reports_dir, "security_issues.json"),
                os.path.join(reports_dir, "bandit_results.json"),
                os.path.join(reports_dir, "vulnerabilities.json")
            ]
            
            for security_file in security_files:
                if os.path.exists(security_file):
                    try:
                        with open(security_file, "r", encoding="utf-8") as f:
                            security_data = json.load(f)
                            if isinstance(security_data, dict):
                                if "results" in security_data:
                                    security_issues = len(security_data["results"])
                                elif "errors" in security_data:
                                    security_issues = len(security_data["errors"])
                                elif "issues" in security_data:
                                    security_issues = len(security_data["issues"])
                            elif isinstance(security_data, list):
                                security_issues = len(security_data)
                        break
                    except:
                        continue
            
            phases["security"] = {"issues": security_issues}
        except Exception as e:
            if self.verbose:
                print(f"Ошибка при загрузке результатов безопасности: {e}")

        # Чтение данных тестового покрытия
        try:
            coverage_file = os.path.join(reports_dir, "coverage.json")
            if os.path.exists(coverage_file):
                with open(coverage_file, "r", encoding="utf-8") as f:
                    coverage_data = json.load(f)
                    if isinstance(coverage_data, dict):
                        # Пытаемся найти общий процент покрытия
                        if "totals" in coverage_data and "percent_covered" in coverage_data["totals"]:
                            test_coverage = coverage_data["totals"]["percent_covered"]
                        elif "coverage" in coverage_data:
                            test_coverage = coverage_data["coverage"]
        except Exception as e:
            if self.verbose:
                print(f"Ошибка при загрузке данных тестового покрытия: {e}")

        # Расчет рейтинга с учетом всех факторов
        rating = self._calculate_rating(code_issues, security_issues, test_coverage)

        # Преобразование рекомендаций в список
        if isinstance(recommendations_text, str):
            recommendations_list = [
                rec.strip() for rec in recommendations_text.split("\n") 
                if rec.strip() and not rec.startswith("#")
            ]
        else:
            recommendations_list = []

        return AuditResult(
            total_issues=code_issues + security_issues,
            code_issues=code_issues,
            security_issues=security_issues,
            test_coverage=test_coverage,
            rating=rating,
            recommendations=recommendations_list,
            phases=phases
        )

    @staticmethod
    def _calculate_rating(code_issues: int, security_issues: int, test_coverage: float = 0.0) -> float:
        """Расчет оценки качества кода с учетом всех факторов"""
        base_rating = 10.0
        
        # Штраф за ошибки кода (0.3 за ошибку)
        code_deduction = 0.3 * code_issues
        
        # Штраф за проблемы безопасности (0.8 за ошибку - более критично)
        security_deduction = 0.8 * security_issues
        
        # Бонус за хорошее тестовое покрытие
        coverage_bonus = 0
        if test_coverage > 80:
            coverage_bonus = 1.0
        elif test_coverage > 60:
            coverage_bonus = 0.5
        elif test_coverage == 0:
            coverage_bonus = -0.5  # Штраф за отсутствие тестов
        
        # Итоговый расчет
        rating = base_rating - code_deduction - security_deduction + coverage_bonus
        rating = max(1, min(10, rating))  # Ограничиваем от 1 до 10
        
        return round(rating, 1)

    def get_status(self) -> Dict[str, Any]:
        """Получение текущего статуса аудита"""
        return {
            "status": self.status.value,
            "progress": self.current_progress,
            "phase": asdict(self.current_phase) if self.current_phase else None,
            "result": asdict(self.result) if self.result else None,
        }
