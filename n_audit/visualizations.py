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
    Отображает анимацию кота с использованием предоставленного ASCII-арта.
    Аргумент progress: целое число от 0 до 100, влияющее на количество отображаемых строк.
    При каждом обновлении предыдущий кадр стирается, создавая эффект анимации.
    """
    # Используем предоставленный ASCII-арт кота
    ascii_cat = [
        ",-.       _,---._ __  / \\",
        " /  )    .-'       `./ /   \\",
        "(  (   ,'            `/    /|",
        " \\  `-\"             \\ '\\   / |",
        "  `.              ,  \\ \\ /  |",
        "   /`.          ,'-`----Y   |",
        "  (            ;        |   '",
        "  |  ,-.    ,-'         |  /",
        "  |  | (   |            | /",
        "  )  |  \\  `.___________|/",
        "  `--'   `--'"
    ]
    
    total_lines = len(ascii_cat)
    # Количество строк, которое будет отображено, зависит от progress
    visible_lines = int(total_lines * progress / 100)
    if visible_lines < 1:
        visible_lines = 1

    # Легкое горизонтальное колебание для эффекта движения
    horizontal_offset = int(2 + 4 * math.sin(math.radians(progress * 5)))
    offset_str = " " * horizontal_offset

    # Очистка экрана и вывод обновленного кадра
    print("\033[H\033[J", end="")  # ANSI-код очистки экрана

    for i in range(visible_lines):
        print(offset_str + ascii_cat[i])
    
    # Прогресс-бар
    bar_width = 40
    filled = int(bar_width * progress / 100)
    bar = '█' * filled + '▒' * (bar_width - filled)
    print(f"\nПрогресс аудита: [{bar}] {progress}%")
    time.sleep(0.3)