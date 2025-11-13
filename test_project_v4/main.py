#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый проект v4 для проверки работы GUI
"""

def greet(name,age):
    """Поздравление"""
    print(f"Hello {name}, you are {age} years old!")
    x=1+2+3+4+5+6+7+8+9+10+11+12+13+14+15+16+17+18+19+20
    print(x)

class Calculator:
    """Калькулятор для простых операций"""
    
    def __init__(self):
        self.value = 0
    
    def add(self, x, y):
        self.value = x + y
        return self.value
    
    def multiply(self,a,b,c,d):
        result=a*b*c*d
        return result
    
    def divide(self, x, y):
        if y == 0:
            raise ValueError("Division by zero!")
        return x / y

# Главная функция
def main():
    calc = Calculator()
    print(calc.add(5, 3))
    greet("John",25)
    result=calc.multiply(2,3,4,5)
    print(result)

if __name__ == '__main__':
    main()
