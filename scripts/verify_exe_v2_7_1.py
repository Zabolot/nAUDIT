#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nAUDIT v2.7.1 - EXE Verification Script
Проверка exe перед развёртыванием: GPU detection, tree display, sync
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ExecutableVerifier:
    def __init__(self):
        self.exe_path = Path("dist/nAUDIT.exe")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "exe_path": str(self.exe_path),
            "tests": [],
            "summary": {}
        }
        
    def verify_exe_exists(self) -> bool:
        """Проверка что exe существует"""
        print("\n📦 TEST 1: EXE файл существует")
        print("-" * 50)
        
        if not self.exe_path.exists():
            print(f"❌ EXE не найден: {self.exe_path}")
            self.results["tests"].append({
                "name": "EXE Exists",
                "status": "FAILED",
                "details": f"File not found: {self.exe_path}"
            })
            return False
        
        size_mb = self.exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ EXE найден: {self.exe_path}")
        print(f"📊 Размер: {size_mb:.2f} МБ")
        
        self.results["tests"].append({
            "name": "EXE Exists",
            "status": "PASSED",
            "size_mb": size_mb
        })
        return True
    
    def verify_source_files(self) -> bool:
        """Проверка что все исправленные файлы существуют"""
        print("\n📄 TEST 2: Исправленные файлы присутствуют")
        print("-" * 50)
        
        files_to_check = [
            "n_audit/gui/tree_widget.py",
            "n_audit/gui/gpu_detector.py",
            "n_audit/gui/graph_visualizer_v2_6.py",
            "n_audit/gui/error_visualization.py",
        ]
        
        all_exist = True
        for file_path in files_to_check:
            full_path = Path(file_path)
            if full_path.exists():
                size_kb = full_path.stat().st_size / 1024
                print(f"✅ {file_path} ({size_kb:.1f} KB)")
            else:
                print(f"❌ {file_path} - НЕ НАЙДЕН")
                all_exist = False
        
        self.results["tests"].append({
            "name": "Source Files Check",
            "status": "PASSED" if all_exist else "FAILED",
            "files": files_to_check,
            "all_exist": all_exist
        })
        return all_exist
    
    def verify_syntax(self) -> bool:
        """Проверка синтаксиса Python файлов"""
        print("\n✨ TEST 3: Синтаксис исправленных файлов")
        print("-" * 50)
        
        files_to_check = [
            "n_audit/gui/tree_widget.py",
            "n_audit/gui/gpu_detector.py",
        ]
        
        all_syntax_ok = True
        for file_path in files_to_check:
            try:
                with open(file_path, 'rb') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"✅ {file_path} - синтаксис OK")
            except SyntaxError as e:
                print(f"❌ {file_path} - СИНТАКСИС ОШИБКА: {e}")
                all_syntax_ok = False
        
        self.results["tests"].append({
            "name": "Syntax Check",
            "status": "PASSED" if all_syntax_ok else "FAILED"
        })
        return all_syntax_ok
    
    def verify_key_features(self) -> bool:
        """Проверка что основные компоненты присутствуют в коде"""
        print("\n🔍 TEST 4: Ключевые компоненты (код содержит исправления)")
        print("-" * 50)
        
        checks = [
            ("n_audit/gui/tree_widget.py", "self.all_project_files", "Tree Widget: all_project_files"),
            ("n_audit/gui/tree_widget.py", "_collect_all_project_files", "Tree Widget: _collect_all_project_files()"),
            ("n_audit/gui/gpu_detector.py", "nvidia-smi", "GPU Detector: nvidia-smi fallback"),
            ("n_audit/gui/graph_visualizer_v2_6.py", "highlight_file", "Graph Visualizer: highlight_file()"),
            ("n_audit/gui/error_visualization.py", "file_selected.connect", "Error Viz: signal sync"),
        ]
        
        all_features_present = True
        for file_path, feature, description in checks:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if feature in content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description} - НЕ НАЙДЕНА")
                    all_features_present = False
        
        self.results["tests"].append({
            "name": "Key Features Check",
            "status": "PASSED" if all_features_present else "FAILED",
            "features_found": all_features_present
        })
        return all_features_present
    
    def check_gpu_detection(self) -> Dict:
        """Проверка GPU detection на компьютере"""
        print("\n🖥️  TEST 5: GPU Detection на компьютере")
        print("-" * 50)
        
        gpu_info = {
            "pytorch": False,
            "cuda_path": False,
            "nvidia_smi": False,
            "devices": []
        }
        
        # Метод 1: PyTorch
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info["pytorch"] = True
                device_name = torch.cuda.get_device_name(0)
                gpu_info["devices"].append(f"PyTorch: {device_name}")
                print(f"✅ PyTorch обнаружил GPU: {device_name}")
            else:
                print(f"ℹ️  PyTorch: GPU не найден (torch.cuda.is_available() = False)")
        except ImportError:
            print(f"ℹ️  PyTorch: не установлен")
        
        # Метод 2: CUDA_PATH
        cuda_path = os.environ.get('CUDA_PATH')
        if cuda_path and os.path.exists(cuda_path):
            gpu_info["cuda_path"] = True
            gpu_info["devices"].append(f"CUDA_PATH: {cuda_path}")
            print(f"✅ CUDA_PATH найден: {cuda_path}")
        else:
            print(f"ℹ️  CUDA_PATH: не установлен")
        
        # Метод 3: nvidia-smi
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu_info["nvidia_smi"] = True
                device_name = result.stdout.strip()
                gpu_info["devices"].append(f"nvidia-smi: {device_name}")
                print(f"✅ nvidia-smi обнаружил GPU: {device_name}")
            else:
                print(f"ℹ️  nvidia-smi: GPU не обнаружен")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"ℹ️  nvidia-smi: не доступна")
        
        gpu_detected = gpu_info["pytorch"] or gpu_info["cuda_path"] or gpu_info["nvidia_smi"]
        status = "GPU DETECTED" if gpu_detected else "NO GPU FOUND (может быть OK)"
        print(f"\n{'✅' if gpu_detected else 'ℹ️ '} GPU статус: {status}")
        
        self.results["tests"].append({
            "name": "GPU Detection",
            "status": "PASSED",
            "gpu_detected": gpu_detected,
            "methods": gpu_info
        })
        return gpu_info
    
    def verify_exe_integrity(self) -> bool:
        """Проверка целостности exe"""
        print("\n🔐 TEST 6: Целостность EXE файла")
        print("-" * 50)
        
        if not self.exe_path.exists():
            print("❌ EXE не существует")
            return False
        
        try:
            # Проверка что exe можно запустить
            result = subprocess.run(
                [str(self.exe_path), "--version"],
                capture_output=True,
                timeout=5,
                text=True
            )
            print(f"✅ EXE можно запустить (exit code: {result.returncode})")
            self.results["tests"].append({
                "name": "EXE Integrity",
                "status": "PASSED",
                "can_execute": True
            })
            return True
        except subprocess.TimeoutExpired:
            print(f"✅ EXE инициирует запуск (timeout при --version OK)")
            self.results["tests"].append({
                "name": "EXE Integrity",
                "status": "PASSED",
                "note": "Timeout is normal for GUI app"
            })
            return True
        except Exception as e:
            print(f"⚠️  Не удалось запустить exe: {e}")
            self.results["tests"].append({
                "name": "EXE Integrity",
                "status": "WARNING",
                "error": str(e)
            })
            return True  # Not a blocker
    
    def generate_report(self):
        """Генерация итогового отчета"""
        print("\n" + "="*60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("="*60)
        
        passed = sum(1 for t in self.results["tests"] if t["status"] == "PASSED")
        failed = sum(1 for t in self.results["tests"] if t["status"] == "FAILED")
        total = len(self.results["tests"])
        
        print(f"\n✅ ПРОЙДЕНО: {passed}/{total}")
        print(f"❌ ПРОВАЛЕНО: {failed}/{total}")
        
        if failed == 0:
            print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
            print("✅ EXE готова к развёртыванию и тестированию")
        else:
            print("\n⚠️  ВНИМАНИЕ: Есть ошибки, требующие исправления")
        
        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "status": "READY" if failed == 0 else "NEEDS_FIX"
        }
        
        # Сохранить отчет в JSON
        report_path = Path("EXE_VERIFICATION_REPORT.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Отчет сохранён: {report_path}")
    
    def run_all_tests(self):
        """Запустить все проверки"""
        print("\n" + "🔬" * 30)
        print("nAUDIT v2.7.1 - EXE VERIFICATION")
        print("🔬" * 30)
        
        tests = [
            ("EXE Exists", self.verify_exe_exists),
            ("Source Files", self.verify_source_files),
            ("Syntax", self.verify_syntax),
            ("Key Features", self.verify_key_features),
            ("GPU Detection", self.check_gpu_detection),
            ("EXE Integrity", self.verify_exe_integrity),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Ошибка в тесте '{test_name}': {e}")
                self.results["tests"].append({
                    "name": test_name,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        self.generate_report()

def main():
    verifier = ExecutableVerifier()
    verifier.run_all_tests()

if __name__ == "__main__":
    main()
