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
    base_cat = [
        "      /\\___/\\         ___          ",
        "     (  o   o  )      (  `---.     ",
        "     (  =^,^=  )       |  |   |    ",
        "      (  T_T  )     ___| ,|, |     ",
        "     .-|     |--.  /    ',|  |     ",
        "    /   \\___/    \\<      ||  |     ",
        "   |               \\     ||  |     ",
        "   |   ||    ||    |    ||  |     ",
        "   |   ||    ||    |     \\  |     ",
        "  (==+=||====||=+==)     |  |     ",
        "   |   ||    ||    |  ___/  |     ",
        "   |   ||    ||    | /     /      ",
        "   |   ||    ||    |/     /       ",
        "   |   ||    ||    |      \\       ",
        "    \\  ||    ||   /   |    \\      ",
        "     \\ ||    || /    |     \\     ",
        "      \\||____||/     |      \\    ",
        "       |      |      |       |    ",
        "       |______|      |_______|    ",
        "      (__)-(__)'     (__)-(__)    "
    ]

    total_lines = len(base_cat)
    visible_lines = int(total_lines * progress / 100)
    if visible_lines < 1:
        visible_lines = 1
    
    horizontal_offset = int(2 + 2 * math.sin(math.radians(progress * 4)))
    offset_str = " " * horizontal_offset

    # Варианты анимации глаз и усов
    cat_variant = base_cat.copy()
    frame = (progress // 5) % 4
    if frame == 0:
        cat_variant[1] = "     (  ◕   ◕  )      (  `---.     "
        cat_variant[2] = "     (  =^.^=  )       |  |   |    "
    elif frame == 1:
        cat_variant[1] = "     (  ⊙   ⊙  )      (  `---.     "
        cat_variant[2] = "     (  =^-^=  )       |  |   |    "
    elif frame == 2:
        cat_variant[1] = "     (  •   •  )      (  `---.     "
        cat_variant[2] = "     (  =^o^=  )       |  |   |    "
    else:
        cat_variant[1] = "     (  ○   ○  )      (  `---.     "
        cat_variant[2] = "     (  =^u^=  )       |  |   |    "

    # Очищаем экран (ANSI escape последовательность) и выводим обновлённый кадр анимации
    print("\033[H\033[J", end="")  # очистка экрана
    for i in range(visible_lines):
        print(offset_str + cat_variant[i])
    for i in range(visible_lines):
        print(offset_str + cat_variant[i])
    print("\033[0m")  # сбрасываем цвет
    
    # Прогресс-бар
    bar_width = 40
    filled = int(bar_width * progress / 100)
    bar = '█' * filled + '▒' * (bar_width - filled)
    print(f"\nПрогресс аудита: [{bar}] {progress}%")
    time.sleep(0.3)