#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфиг проекта
"""

DEBUG = True
SECRET_KEY = "hardcoded_secret_key_123"  # Проблема безопасности!
DATABASE_URL = "postgresql://user:password@localhost/db"  # Проблема безопасности!

API_TIMEOUT = 30
MAX_RETRIES=3
LOG_LEVEL="DEBUG"
