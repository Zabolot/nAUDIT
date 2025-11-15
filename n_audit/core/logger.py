#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nAUDIT v2.7 - Enhanced Logging System
Улучшенная система логирования для диагностики проблем
"""

import sys
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Форматер логов с цветом для консоли"""
    
    # ANSI цветовые коды
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)

class LoggerManager:
    """Менеджер логирования для всей программы"""
    
    _instance = None
    _loggers = {}
    _file_handler = None
    _console_handler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._setup_logging()
    
    def _setup_logging(self):
        """Настраивает логирование"""
        # Создаем папку для логов
        log_dir = Path.home() / ".naudit" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Путь к файлу лога
        log_file = log_dir / f"naudit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Корневой логгер
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Файловый обработчик (verbose)
        self._file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self._file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._file_handler.setFormatter(file_formatter)
        root_logger.addHandler(self._file_handler)
        
        # Консольный обработчик
        self._console_handler = logging.StreamHandler(sys.stdout)
        self._console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '[%(levelname)s] %(message)s'
        )
        self._console_handler.setFormatter(console_formatter)
        root_logger.addHandler(self._console_handler)
        
        # Логируем начало программы
        root_logger.info(f"nAUDIT v2.7 logging initialized")
        root_logger.info(f"Log file: {log_file}")
        root_logger.debug(f"Python: {sys.version}")
        root_logger.debug(f"Platform: {sys.platform}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Получает логгер для модуля"""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]
    
    def set_console_level(self, level: str):
        """Устанавливает уровень логирования консоли"""
        if self._console_handler:
            self._console_handler.setLevel(getattr(logging, level.upper()))
    
    @staticmethod
    def get_log_path() -> Path:
        """Возвращает пусть к папке логов"""
        return Path.home() / ".naudit" / "logs"

# Глобальный менеджер логирования
_logger_manager = None

def init_logging():
    """Инициализирует логирование"""
    global _logger_manager
    _logger_manager = LoggerManager()

def get_logger(name: str) -> logging.Logger:
    """Получает логгер для модуля"""
    if _logger_manager is None:
        init_logging()
    return _logger_manager.get_logger(name)

# Для удобства - создаем логгер модуля
logger = get_logger(__name__)
