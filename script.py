import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Список файлов для сравнения (sequential)
file_paths = [
    Path("mysql/mysql (sequential u1)/phase_summary.csv"),
    Path("postgres/postgres (sequential u1)/phase_summary.csv"),
    Path("redis/redis (sequential u1)/phase_summary_client.csv"),
    Path("sqlite/sqlite (sequential u1)/phase_summary.csv")
]

dfs = []
labels = []

# Считываем данные и строго фильтруем по фазе benchmark
for path in file_paths:
    df = pd.read_csv(path)
    
    # Приводим к нижнему регистру и убираем лишние пробелы для гарантии, что берем именно benchmark
    df_benchmark = df[df['phase'].astype(str).str.lower().str.strip() == 'benchmark'].copy()
    
    # Извлекаем число после q (например, 10 из q10_...) для естественной (числовой) сортировки
    df_benchmark['q_num'] = df_benchmark['query_name'].str.extract(r'q(\d+)').astype(int)
    df_benchmark = df_benchmark.sort_values('q_num').drop(columns=['q_num']).reset_index(drop=True)
    
    dfs.append(df_benchmark)
    
    # Берем первое слово из названия папки (mysql, postgres, и т.д.)
    db_name = path.parent.name.split()[0]
    labels.append(db_name)

# Собираем уникальные запросы 
query_names = dfs[0]['query_name'].values

plt.figure(figsize=(20, 8))

# Цвета для разных баз данных
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
bar_width = 0.2
x_indexes = np.arange(len(query_names))

bars_list = []
max_y = 0

# Строим столбцы для каждой базы данных (сравниваем ops_per_sec)
for i, df_bench in enumerate(dfs):
    pos = x_indexes + i * bar_width
    bars = plt.bar(pos, df_bench['ops_per_sec'], width=bar_width, color=colors[i], label=labels[i])
    bars_list.append(bars)
    
    current_max = df_bench['ops_per_sec'].max()
    if pd.notna(current_max) and current_max > max_y:
        max_y = current_max

# Явно укажем в заголовке метрику Ops/sec и добавим отступ
plt.title('Comparison: Operations per Second (Ops/sec) (Sequential u1)', fontsize=16, pad=20)

# Центрируем подписи по оси x (4 столбца)
plt.xticks(x_indexes + bar_width * 1.5, query_names, rotation=45, ha='right')

# Логарифмическая шкала
plt.yscale('log')

# Увеличиваем лимит по оси Y, чтобы добавить пустое пространство над столбцами
if max_y > 0:
    plt.ylim(top=max_y * 50)

plt.xlabel('')
plt.ylabel('')
plt.yticks([])

# Убираем рамки
ax = plt.gca()
for spine in ax.spines.values():
    spine.set_visible(False)

# Добавляем цифры над каждым столбиком
for metric_bars in bars_list:
    for bar in metric_bars:
        yval = bar.get_height()
        
        if pd.isna(yval) or yval <= 0:
            continue
            
        if yval == int(yval):
            val_text = f'{int(yval)}'
        else:
            val_text = f'{yval:.2f}' if yval < 1000 else f'{yval:,.0f}'
        
        plt.text(bar.get_x() + bar.get_width()/2, yval * 1.15, val_text, ha='center', va='bottom', rotation=90, fontsize=12)

# Увеличиваем размер шрифта легенды
plt.legend(loc='upper right', fontsize=16)
plt.tight_layout()
plt.show()