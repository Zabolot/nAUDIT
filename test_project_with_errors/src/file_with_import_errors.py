# Файл с проблемами импортирования
import non_existent_module_xyz  # Модуль не существует
from another_fake_module import FakeClass

def process_data(data):
    """Функция с неиспользуемыми переменными"""
    unused_var = 42
    another_unused = "test"
    return sum(data)

# Циклический импорт
from . import file_with_circular_import
