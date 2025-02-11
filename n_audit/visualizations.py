import os
import time
import math

def generate_visualizations(reports_dir):
    print("[*] Генерация визуализаций...")
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
        
        G = nx.DiGraph()
        G.add_node("start")
        G.add_node("end")
        G.add_edge("start", "end")
        
        plt.figure(figsize=(10, 7))
        nx.draw(G, with_labels=True, node_size=3000)
        img_path = os.path.join(reports_dir, "dependency_graph.png")
        plt.savefig(img_path)
        print(f"[*] Визуализация сохранена: {img_path}")
    except ImportError:
        print("[WARNING] Не установлены необходимые модули для генерации визуализаций.")

def display_cat_animation(progress):
    """
    Плавное появление кота из ничего в одном месте с лёгкой анимацией движения.
    При каждом обновлении предыдущий кадр стирается.
    Аргумент progress: целое число от 0 до 100, влияющее на степень появления кота и динамику.
    """
    # Базовый ASCII-арт кота (10 строк)
    base_cat = [
        "               /\\     /\\",
        "              {  `---'  }",
        "              {  O   O  }",
        "              ~~>  V  <~~",
        "               \\  \\|/  /",
        "                `-----'____",
        "                /     \\    \\_",
        "               {       }\\  )_\\_   _",
        "               |  \\_/  |/ /  \\_\\_/ )",
        "                \\__/  /(_/     \\__/",
        "                  (__/"
    ]
    total_lines = len(base_cat)
    # Определяем количество отображаемых строк в зависимости от progress
    visible_lines = int(total_lines * progress / 100)
    if visible_lines < 1:
        visible_lines = 1
    
    # Лёгкая анимация движения: смещение по горизонтали (значение осциллирует)
    horizontal_offset = int(3 + 3 * math.sin(math.radians(progress * 4)))
    offset_str = " " * horizontal_offset

    # Эффект смены деталей: пусть каждые 10% progress меняется вариант "глаз"
    if (progress // 10) % 2 == 0:
        cat_variant = base_cat.copy()
        # Меняем символы глаз
        cat_variant[2] = "              {  o   o  }"
    else:
        cat_variant = base_cat.copy()

    # Очищаем экран (ANSI escape последовательность) и выводим обновлённый кадр анимации
    print("\033[H\033[J", end="")  # очистка экрана
    for i in range(visible_lines):
        print(offset_str + cat_variant[i])
    
    # Прогресс-бар
    bar_width = 40
    filled = int(bar_width * progress / 100)
    bar = '█' * filled + '▒' * (bar_width - filled)
    print(f"\nПрогресс аудита: [{bar}] {progress}%")
    time.sleep(0.3)