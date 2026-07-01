"""
可视化工具
Agent 通过这些工具自动生成图表
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端，用于服务器环境
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

from tools.data_tools import _load_data

# ============================================================
# 中文字体配置
# ============================================================
def _setup_chinese_font():
    """配置 matplotlib 中文显示"""
    # 尝试常见的 Windows 中文字体
    chinese_fonts = [
        'Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong',
        'SimSun', 'NSimSun', 'STSong', 'PingFang SC'
    ]
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    for font in chinese_fonts:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font, 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            return font
    # 如果没有中文字体，回退到默认
    plt.rcParams['axes.unicode_minus'] = False
    return 'DejaVu Sans'


_used_font = _setup_chinese_font()

CHART_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "charts")
os.makedirs(CHART_DIR, exist_ok=True)


def _save_and_close(title: str) -> str:
    """保存图表并关闭，返回保存路径"""
    safe_title = title.replace(" ", "_").replace("/", "_")
    path = os.path.join(CHART_DIR, f"{safe_title}.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def draw_bar(file_path: str, x_col: str, y_col: str, title: str = "柱状图") -> str:
    """
    绘制柱状图：适合分类对比

    参数:
        file_path: 数据文件路径
        x_col: X 轴列名（分类列）
        y_col: Y 轴列名（数值列）
        title: 图表标题
    """
    df = _load_data(file_path)
    # 如果分类太多，只取前20
    if df[x_col].nunique() > 20:
        grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(20)
    else:
        grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(grouped)), grouped.values, color='#4A90D9', alpha=0.85)
    ax.set_xticks(range(len(grouped)))
    ax.set_xticklabels(grouped.index, rotation=45, ha='right', fontsize=9)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel(y_col)
    ax.set_xlabel(x_col)

    # 在柱子上标注数值
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}', ha='center', va='bottom', fontsize=8)

    return _save_and_close(f"bar_{title}")


def draw_line(file_path: str, x_col: str, y_col: str, title: str = "折线图") -> str:
    """
    绘制折线图：适合趋势展示

    参数:
        file_path: 数据文件路径
        x_col: X 轴列名（通常是时间/顺序列）
        y_col: Y 轴列名（数值列）
        title: 图表标题
    """
    df = _load_data(file_path)
    grouped = df.groupby(x_col)[y_col].sum().sort_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(range(len(grouped)), grouped.values, color='#E74C3C', linewidth=2, marker='o', markersize=4)
    ax.set_xticks(range(0, len(grouped), max(1, len(grouped)//10)))
    ax.set_xticklabels(grouped.index[::max(1, len(grouped)//10)], rotation=45, ha='right', fontsize=9)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel(y_col)
    ax.set_xlabel(x_col)
    ax.grid(True, alpha=0.3)

    return _save_and_close(f"line_{title}")


def draw_box(file_path: str, column: str, group_col: str = None, title: str = "箱线图") -> str:
    """
    绘制箱线图：展示数据分布和异常值

    参数:
        file_path: 数据文件路径
        column: 要分析的数值列
        group_col: 分组列（可选，按此列分组绘制多个箱线图）
        title: 图表标题
    """
    df = _load_data(file_path)

    fig, ax = plt.subplots(figsize=(12, 6))
    if group_col and group_col in df.columns:
        df.boxplot(column=column, by=group_col, ax=ax)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.suptitle('')
    else:
        ax.boxplot(df[column].dropna())
        ax.set_xticklabels([column])
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel(column)

    return _save_and_close(f"box_{title}")


def draw_heatmap(file_path: str, title: str = "相关性热力图") -> str:
    """
    绘制热力图：展示数值列之间的相关性

    参数:
        file_path: 数据文件路径
        title: 图表标题
    """
    df = _load_data(file_path)
    numeric_df = df.select_dtypes(include=['number'])
    corr = numeric_df.corr()

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(corr.values, cmap='RdYlBu_r', vmin=-1, vmax=1, aspect='auto')

    # 标注相关系数
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                    ha='center', va='center',
                    fontsize=9,
                    color='white' if abs(corr.iloc[i, j]) > 0.5 else 'black')

    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(corr.columns, fontsize=9)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.colorbar(im, ax=ax, shrink=0.8)

    return _save_and_close(f"heatmap_{title}")


def draw_scatter(file_path: str, x_col: str, y_col: str, title: str = "散点图") -> str:
    """
    绘制散点图：展示两个数值变量的关系

    参数:
        file_path: 数据文件路径
        x_col: X 轴列名
        y_col: Y 轴列名
        title: 图表标题
    """
    df = _load_data(file_path)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(df[x_col], df[y_col], alpha=0.5, c='#3498DB', edgecolors='white', s=30)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.grid(True, alpha=0.3)

    return _save_and_close(f"scatter_{title}")


def draw_pie(file_path: str, label_col: str, value_col: str, title: str = "饼图") -> str:
    """
    绘制饼图：展示占比

    参数:
        file_path: 数据文件路径
        label_col: 标签列名
        value_col: 数值列名
        title: 图表标题
    """
    df = _load_data(file_path)
    grouped = df.groupby(label_col)[value_col].sum().sort_values(ascending=False)

    # 如果分类太多，合并小类为"其他"
    if len(grouped) > 8:
        top = grouped.head(7)
        other = grouped.iloc[7:].sum()
        grouped = pd.concat([top, pd.Series({'其他': other})])

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.Set3(range(len(grouped)))
    wedges, texts, autotexts = ax.pie(
        grouped.values, labels=grouped.index, autopct='%1.1f%%',
        colors=colors, startangle=90, pctdistance=0.85
    )
    ax.set_title(title, fontsize=14, fontweight='bold')

    return _save_and_close(f"pie_{title}")
