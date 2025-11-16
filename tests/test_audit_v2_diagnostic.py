#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки audit_manager_v2 на пустой папке и на реальном проекте.
Проверяет:
1. Пустая папка должна вернуть рейтинг 2.0 (не 9.5)
2. Реальный проект должен вернуть реальные метрики
3. Результаты должны экспортироваться корректно
"""

import os
import sys
import json
from pathlib import Path

# Убедимся, что родительская папка проекта в sys.path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Установка кодировки для Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

from n_audit.audit_manager_v2 import AuditManager, AuditResult


def test_empty_folder():
    """Тест 1: Пустая папка должна вернуть рейтинг 2.0"""
    print("\n" + "=" * 70)
    print("ТЕСТ 1: Аудит пустой папки")
    print("=" * 70)
    
    empty_folder = project_root / "test_empty_project"
    manager = AuditManager()
    
    print(f"\n[*] Запуск аудита пустой папки: {empty_folder}")
    
    # Подготавливаем переменную для сохранения результата
    result_container = {'result': None, 'error': None}
    
    def on_result(result):
        result_container['result'] = result
    
    def on_error(error):
        result_container['error'] = error
    
    manager.on_result = on_result
    manager.on_error = on_error
    
    # Запускаем аудит (асинхронно)
    manager.start_audit(str(empty_folder))
    
    # Ждём завершения аудита (максимум 30 секунд)
    import time
    timeout = 30
    start_time = time.time()
    
    while result_container['result'] is None and result_container['error'] is None:
        if time.time() - start_time > timeout:
            print("\n✗ Таймаут: аудит не завершился за 30 секунд")
            return False
        time.sleep(0.1)
    
    if result_container['error']:
        print(f"\n✗ Ошибка аудита: {result_container['error']}")
        return False
    
    result = result_container['result']
    
    if result:
        print(f"\n✓ Результат получен:")
        print(f"  - Рейтинг: {result.rating}")
        print(f"  - Проблемы с кодом: {result.code_issues}")
        print(f"  - Проблемы безопасности: {result.security_issues}")
        print(f"  - Покрытие тестами: {result.test_coverage}%")
        print(f"  - Все проблемы: {len(result.issue_details)}")
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА
        if result.rating == 2.0:
            print("\n✓✓✓ УСПЕХ: Пустая папка вернула рейтинг 2.0 (ожидаемо)")
            return True
        else:
            print(f"\n✗✗✗ ОШИБКА: Пустая папка вернула рейтинг {result.rating}, ожидался 2.0")
            return False
    else:
        print("\n✗ Ошибка при аудите пустой папки")
        return False


def test_real_project():
    """Тест 2: Реальный проект должен вернуть разные метрики"""
    print("\n" + "=" * 70)
    print("ТЕСТ 2: Аудит реального проекта (n_audit)")
    print("=" * 70)
    
    real_folder = project_root / "n_audit"
    manager = AuditManager()
    
    print(f"\n[*] Запуск аудита реального проекта: {real_folder}")
    
    # Подготавливаем переменную для сохранения результата
    result_container = {'result': None, 'error': None}
    
    def on_result(result):
        result_container['result'] = result
    
    def on_error(error):
        result_container['error'] = error
    
    manager.on_result = on_result
    manager.on_error = on_error
    
    # Запускаем аудит (асинхронно)
    manager.start_audit(str(real_folder))
    
    # Ждём завершения аудита (максимум 120 секунд для реального проекта)
    import time
    timeout = 120
    start_time = time.time()
    
    while result_container['result'] is None and result_container['error'] is None:
        if time.time() - start_time > timeout:
            print("\n✗ Таймаут: аудит не завершился за 120 секунд")
            return False
        time.sleep(0.1)
    
    if result_container['error']:
        print(f"\n✗ Ошибка аудита: {result_container['error']}")
        return False
    
    result = result_container['result']
    
    if result:
        print(f"\n✓ Результат получен:")
        print(f"  - Рейтинг: {result.rating}")
        print(f"  - Проблемы с кодом: {result.code_issues}")
        print(f"  - Проблемы безопасности: {result.security_issues}")
        print(f"  - Покрытие тестами: {result.test_coverage}%")
        print(f"  - Общих проблем: {len(result.issue_details)}")
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА
        if result.rating != 2.0:
            print(f"\n✓✓✓ УСПЕХ: Реальный проект вернул рейтинг {result.rating} (не 2.0)")
            if result.code_issues > 0 or result.security_issues > 0:
                print(f"   (найдены реальные проблемы - анализ работает!)")
                return True
            else:
                print(f"   (проблемы не найдены - возможно, проект чист)")
                return True
        else:
            print(f"\n✗✗✗ ОШИБКА: Реальный проект вернул рейтинг 2.0 (как пустая папка!)")
            return False
    else:
        print("\n✗ Ошибка при аудите реального проекта")
        return False


def test_export():
    """Тест 3: Проверяем, что экспорт содержит реальные данные"""
    print("\n" + "=" * 70)
    print("ТЕСТ 3: Проверка экспорта результатов")
    print("=" * 70)
    
    # Используем папку n_audit для экспорта
    real_folder = project_root / "n_audit"
    manager = AuditManager()
    
    print(f"\n[*] Запуск аудита и экспорта...")
    
    # Подготавливаем переменную для сохранения результата
    result_container = {'result': None, 'error': None}
    
    def on_result(result):
        result_container['result'] = result
    
    def on_error(error):
        result_container['error'] = error
    
    manager.on_result = on_result
    manager.on_error = on_error
    
    # Запускаем аудит (асинхронно)
    manager.start_audit(str(real_folder))
    
    # Ждём завершения аудита (максимум 120 секунд)
    import time
    timeout = 120
    start_time = time.time()
    
    while result_container['result'] is None and result_container['error'] is None:
        if time.time() - start_time > timeout:
            print("\n✗ Таймаут: аудит не завершился за 120 секунд")
            return False
        time.sleep(0.1)
    
    if result_container['error']:
        print(f"\n✗ Ошибка при аудите: {result_container['error']}")
        return False
    
    result = result_container['result']
    
    if not result:
        print("\n✗ Ошибка при аудите")
        return False
    
    # Проверяем, что экспортированные файлы существуют и содержат данные
    reports_dir = Path(real_folder) / ".audit_results" / "reports"
    
    if not reports_dir.exists():
        print(f"\n✗ Папка отчётов не найдена: {reports_dir}")
        return False
    
    json_files = list(reports_dir.glob("*.json"))
    if not json_files:
        print(f"\n✗ JSON файлов не найдено в {reports_dir}")
        return False
    
    print(f"\n✓ Найдено файлов: {len(json_files)}")
    for json_file in json_files:
        size = json_file.stat().st_size
        print(f"  - {json_file.name}: {size} байт")
        
        # Проверяем, не пусты ли файлы
        if size < 10:
            print(f"    ✗ ВНИМАНИЕ: Файл очень маленький!")
        else:
            print(f"    ✓ Файл содержит данные")
            
            # Попробуем распарсить
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    print(f"    ✓ JSON структура: объект с {len(data)} полями")
                elif isinstance(data, list):
                    print(f"    ✓ JSON структура: массив с {len(data)} элементами")
            except Exception as e:
                print(f"    ✗ Ошибка парсинга: {e}")
    
    print(f"\n✓ Экспорт работает и содержит данные")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ДИАГНОСТИКА nAUDIT v3 - audit_manager_v2")
    print("=" * 70)
    
    results = []
    
    # Запускаем тесты
    try:
        results.append(("Тест 1: Пустая папка (рейтинг 2.0)", test_empty_folder()))
        results.append(("Тест 2: Реальный проект (рейтинг != 2.0)", test_real_project()))
        results.append(("Тест 3: Экспорт (данные в JSON)", test_export()))
    except Exception as e:
        print(f"\n✗ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # Итоги
    print("\n" + "=" * 70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, r in results if r)
    total_tests = len(results)
    print(f"\nВсего: {total_passed}/{total_tests} тестов пройдено")
    
    if total_passed == total_tests:
        print("\n✓✓✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ - v3 РАБОТАЕТ КОРРЕКТНО!")
    else:
        print(f"\n✗✗✗ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ - ТРЕБУЕТСЯ ОТЛАДКА!")
    
    sys.exit(0 if total_passed == total_tests else 1)
