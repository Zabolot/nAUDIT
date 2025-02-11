import os
import time

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
    Вывод анимации большого кота с эффектом заполнения сверху вниз.
    progress: целое число от 0 до 100.
    """
    # ASCII-арт большого кота
    cat_art = [
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
    total_lines = len(cat_art)
    filled_count = int(total_lines * progress / 100)
    
    # Формирование нового изображения: первые filled_count строк заменяем на заполнённые блоком
    filled_cat = []
    for i, line in enumerate(cat_art):
        if i < filled_count:
            # Создаем строку заполненную блоками той же длины, сохраняя отступы
            indent = len(line) - len(line.lstrip())
            filled_line = " " * indent + "█" * (len(line.lstrip()))
            filled_cat.append(filled_line)
        else:
            filled_cat.append(line)
    
    # Очищаем экран и выводим изображение
    print("\033[H\033[J", end="")  # ANSI-очистка экрана
    for line in filled_cat:
        print(line)
    print(f"\nПрогресс аудита: {progress}%")
    time.sleep(0.5)  # задержка для наглядности