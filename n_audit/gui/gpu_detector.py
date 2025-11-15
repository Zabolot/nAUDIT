#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU Detector & System Optimization Module

Обнаруживает доступные ресурсы GPU и оптимизирует рендеринг графов
для быстрого и эффективного отображения
"""

import sys
import platform
import psutil
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """Информация о GPU"""
    name: str
    memory_mb: int
    compute_capability: Optional[str] = None
    driver_version: Optional[str] = None
    is_available: bool = False
    
    def __str__(self):
        return f"{self.name} ({self.memory_mb} MB)"


@dataclass
class SystemResources:
    """Системные ресурсы для оптимизации"""
    cpu_count: int
    total_memory_gb: float
    available_memory_gb: float
    gpu_available: bool
    gpu_info: Optional[GPUInfo] = None
    os_name: str = ""
    
    def get_optimization_level(self) -> str:
        """Определяет уровень оптимизации на основе ресурсов"""
        # HIGH: Мощный ПК с GPU и 16+ GB RAM
        if self.gpu_available and self.available_memory_gb > 12:
            return "HIGH"
        # MEDIUM: Среднее оборудование с 8+ GB RAM
        if self.available_memory_gb > 7:
            return "MEDIUM"
        # LOW: Слабое оборудование
        return "LOW"


class GPUDetector:
    """Обнаруживает GPU и возвращает информацию о системе"""
    
    @staticmethod
    def detect_gpu() -> Tuple[bool, Optional[GPUInfo]]:
        """Попытается обнаружить NVIDIA GPU через CUDA"""
        # Способ 1: PyTorch CUDA
        try:
            import torch
            
            logger.debug(f"PyTorch версия: {torch.__version__}")
            logger.debug(f"CUDA доступна: {torch.cuda.is_available()}")
            logger.debug(f"cuDNN версия: {torch.backends.cudnn.version()}")
            
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                logger.debug(f"Количество GPU устройств: {device_count}")
                
                for i in range(device_count):
                    try:
                        name = torch.cuda.get_device_name(i)
                        properties = torch.cuda.get_device_properties(i)
                        total_memory = properties.total_memory / 1024 / 1024
                        
                        logger.info(f"✓ GPU {i}: {name}, {total_memory:.0f} MB")
                        
                        return True, GPUInfo(
                            name=name,
                            memory_mb=int(total_memory),
                            compute_capability=f"{properties.major}.{properties.minor}",
                            driver_version=torch.version.cuda,
                            is_available=True
                        )
                    except Exception as e:
                        logger.debug(f"Ошибка при чтении GPU {i}: {e}")
                        continue
            else:
                logger.debug("⚠ CUDA доступна через PyTorch, но нет устройств")
                
        except ImportError:
            logger.debug("PyTorch не установлен, GPU acceleration недоступна")
        except Exception as e:
            logger.debug(f"Ошибка при обнаружении CUDA через PyTorch: {type(e).__name__}: {e}")
        
        # Способ 2: Прямая проверка через nvidia-smi (fallback)
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                line = result.stdout.strip().split('\n')[0]
                parts = line.split(',')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    memory_str = parts[1].strip()
                    memory_mb = int(memory_str.split()[0])
                    
                    logger.info(f"✓ GPU найден через nvidia-smi: {name}, {memory_mb} MB")
                    
                    return True, GPUInfo(
                        name=name,
                        memory_mb=memory_mb,
                        is_available=True
                    )
        except Exception as e:
            logger.debug(f"nvidia-smi недоступен: {type(e).__name__}")
        
        logger.debug("GPU не обнаружен")
        return False, None
    
    @staticmethod
    def get_system_resources() -> SystemResources:
        """Собирает информацию о системных ресурсах"""
        # CPU и память
        cpu_count = psutil.cpu_count(logical=False) or 1
        memory = psutil.virtual_memory()
        
        # Попытка найти GPU
        gpu_available, gpu_info = GPUDetector.detect_gpu()
        
        os_name = platform.system()
        
        resources = SystemResources(
            cpu_count=cpu_count,
            total_memory_gb=memory.total / 1024 / 1024 / 1024,
            available_memory_gb=memory.available / 1024 / 1024 / 1024,
            gpu_available=gpu_available,
            gpu_info=gpu_info,
            os_name=os_name
        )
        
        return resources
    
    @staticmethod
    def get_optimization_hints(resources: SystemResources) -> Dict[str, any]:
        """Возвращает рекомендации по оптимизации"""
        level = resources.get_optimization_level()
        
        hints = {
            "optimization_level": level,
            "use_gpu": resources.gpu_available,
            "use_threading": resources.cpu_count > 2,
            "cache_enabled": resources.available_memory_gb > 4,
        }
        
        # Параметры для рендеринга графов
        if level == "HIGH":
            hints.update({
                "spring_iterations": 100,  # Больше итераций для лучшей компоновки
                "max_nodes_per_graph": 5000,
                "enable_animations": True,
                "batch_processing": True,
            })
        elif level == "MEDIUM":
            hints.update({
                "spring_iterations": 50,
                "max_nodes_per_graph": 2000,
                "enable_animations": True,
                "batch_processing": False,
            })
        else:  # LOW
            hints.update({
                "spring_iterations": 30,
                "max_nodes_per_graph": 1000,
                "enable_animations": False,
                "batch_processing": False,
            })
        
        return hints


def print_system_info():
    """Выводит информацию о системе (для отладки)"""
    resources = GPUDetector.get_system_resources()
    
    print("\n" + "="*60)
    print("ИНФОРМАЦИЯ О СИСТЕМЕ")
    print("="*60)
    print(f"OS:                    {resources.os_name}")
    print(f"CPU cores:             {resources.cpu_count}")
    print(f"Total Memory:          {resources.total_memory_gb:.2f} GB")
    print(f"Available Memory:      {resources.available_memory_gb:.2f} GB")
    print(f"GPU Available:         {'Да' if resources.gpu_available else 'Нет'}")
    if resources.gpu_info:
        print(f"GPU Model:             {resources.gpu_info.name}")
        print(f"GPU Memory:            {resources.gpu_info.memory_mb} MB")
        if resources.gpu_info.compute_capability:
            print(f"Compute Capability:    {resources.gpu_info.compute_capability}")
    
    print(f"\nУровень оптимизации:   {resources.get_optimization_level()}")
    
    hints = GPUDetector.get_optimization_hints(resources)
    print(f"\nРекомендации оптимизации:")
    for key, value in hints.items():
        if key != "optimization_level":
            print(f"  {key:30} {value}")
    print("="*60 + "\n")


if __name__ == "__main__":
    print_system_info()
