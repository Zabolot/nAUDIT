#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест функциональности приложения через интерфейс
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("🧪 ТЕСТ ФУНКЦИОНАЛЬНОСТИ nAUDIT v4.0")
print("="*70)

# 1. Тестируем AuditEngine
print("\n1️⃣  ТЕСТ AuditEngine:")
print("-"*70)

try:
    from n_audit.audit_engine import AuditEngine
    
    # Создаем тестовый проект
    test_project = Path("test_project_v4")
    if not test_project.exists():
        test_project.mkdir(exist_ok=True)
        (test_project / "test.py").write_text("x = 1\ny = 2\nprint(x + y)")
    
    engine = AuditEngine(test_project)
    print(f"✅ AuditEngine создан для {test_project}")
    
    # Пытаемся запустить аудит
    print("   Запуск аудита...")
    report = engine.analyze()
    print(f"✅ Аудит завершен")
    print(f"   - Ошибок найдено: {len(report.get('issues', []))}")
    print(f"   - Файлов проверено: {len(report.get('files', []))}")
    
except Exception as e:
    print(f"❌ AuditEngine: {e}")
    import traceback
    traceback.print_exc()

# 2. Тестируем ReportGenerator
print("\n2️⃣  ТЕСТ ReportGenerator:")
print("-"*70)

try:
    from n_audit.report_generator import ReportGenerator
    
    if 'report' in locals():
        generator = ReportGenerator(report)
        print(f"✅ ReportGenerator создан")
        
        # HTML отчет
        html = generator.generate_html()
        print(f"✅ HTML отчет сгенерирован ({len(html)} байт)")
        
        # JSON отчет
        json_str = generator.generate_json()
        print(f"✅ JSON отчет сгенерирован ({len(json_str)} байт)")
    
except Exception as e:
    print(f"❌ ReportGenerator: {e}")
    import traceback
    traceback.print_exc()

# 3. Тестируем RecommendationsEngine
print("\n3️⃣  ТЕСТ RecommendationsEngine:")
print("-"*70)

try:
    from n_audit.recommendations_engine import RecommendationsEngine
    
    if 'report' in locals():
        rec_engine = RecommendationsEngine(report)
        print(f"✅ RecommendationsEngine создан")
        
        recommendations = rec_engine.generate_recommendations()
        print(f"✅ Рекомендации сгенерированы: {len(recommendations)} шт.")
    
except Exception as e:
    print(f"❌ RecommendationsEngine: {e}")
    import traceback
    traceback.print_exc()

# 4. Тестируем GUI компоненты (без отображения)
print("\n4️⃣  ТЕСТ GUI КОМПОНЕНТОВ:")
print("-"*70)

try:
    from PyQt6.QtWidgets import QApplication
    import os
    
    # Отключаем отображение
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    print("✅ QApplication создан")
    
    from n_audit.gui.error_visualization import ErrorVisualizationWidget
    from n_audit.gui.tree_widget import ErrorTreeWidget
    from n_audit.gui.metrics_visualizer import MetricsVisualizer
    from n_audit.gui.graph_visualizer import GraphVisualizerWidget
    
    # Создаем виджеты
    error_viz = ErrorVisualizationWidget()
    print("✅ ErrorVisualizationWidget создан")
    
    tree = ErrorTreeWidget()
    print("✅ ErrorTreeWidget создан")
    
    metrics = MetricsVisualizer()
    print("✅ MetricsVisualizer создан")
    
    graph = GraphVisualizerWidget()
    print("✅ GraphVisualizerWidget создан")
    
    # Загружаем данные если есть
    if 'report' in locals():
        print("   Загрузка данных в виджеты...")
        error_viz.populate_from_report(report)
        print("   ✓ ErrorVisualizationWidget заполнен")
        
        tree.populate_from_report(report)
        print("   ✓ ErrorTreeWidget заполнен")
    
except Exception as e:
    print(f"❌ GUI компоненты: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("="*70 + "\n")
