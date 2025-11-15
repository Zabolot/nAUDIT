# Чистый файл без ошибок
def process_string(text: str) -> str:
    """Обрабатывает строку"""
    return text.upper()

def calculate_average(numbers: list) -> float:
    """Вычисляет среднее значение"""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, a: int, b: int) -> int:
        self.result = a + b
        return self.result
    
    def multiply(self, a: int, b: int) -> int:
        self.result = a * b
        return self.result

if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(5, 3))
    print(calc.multiply(4, 7))
