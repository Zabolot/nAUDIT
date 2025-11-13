#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль утилит - тестовый файл для проверки анализатора
"""

import os
import sys

def unsafe_function():
    """Функция с проблемами безопасности"""
    import pickle
    user_input = input("Enter data: ")
    data = pickle.loads(user_input)  # Проблема безопасности!
    return data


def badly_formatted():
    x=1
    y=2
    z=x+y
    result = z*2
    if result > 10:
        print("Result is big")
    else:
        print("Result is small")
    return result


class DataProcessor:
    """Обработчик данных с проблемами"""
    
    def __init__(self):
        self.data = None
    
    def process(self,input_data,flag1,flag2,flag3):
        """Обработка с множеством параметров"""
        if flag1:
            self.data = input_data.strip()
        elif flag2:
            self.data = input_data.upper()
        elif flag3:
            self.data = input_data.lower()
        else:
            self.data = input_data
        return self.data
