# Файл с проблемами типов
def add_numbers(a: int, b: int) -> int:
    """Функция для сложения"""
    return a + b

# Вызов с неправильным типом
result = add_numbers("text", 5)  # Ошибка: передаю строку вместо int

class MyClass:
    def __init__(self):
        self.value = 10
    
    def get_value(self) -> int:
        return self.value
    
    def set_value(self, val: str):  # Ожидается str
        self.value = val

# Неправильный вызов метода
obj = MyClass()
obj.set_value(123)  # Ошибка: передаю int вместо str
