"""
数据读取工具
Agent 通过这些工具读取用户上传的 CSV/Excel 文件
"""
import pandas as pd
import os

# 全局缓存：避免每次工具调用都重新读取文件
_data_cache = {}


def _load_data(file_path: str) -> pd.DataFrame:
    """带缓存的数据加载，避免重复读取"""
    if file_path not in _data_cache:
        if file_path.endswith('.csv'):
            _data_cache[file_path] = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            _data_cache[file_path] = pd.read_excel(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path}")
    return _data_cache[file_path]


def get_data_info(file_path: str) -> str:
    """
    获取数据的基本信息：行列数、列名、数据类型、前5行预览

    这是 Agent 了解数据的第一步，相当于 "看一眼数据长什么样"

    参数:
        file_path: CSV 或 Excel 文件路径
    返回:
        包含数据基本信息的文本
    """
    df = _load_data(file_path)
    info_lines = [
        f"📊 数据基本信息",
        f"- 行数: {len(df)}",
        f"- 列数: {len(df.columns)}",
        f"- 列名: {list(df.columns)}",
        f"- 数据类型:\n{df.dtypes.to_string()}",
        f"\n📋 前5行预览:\n{df.head().to_string()}",
        f"\n📊 描述统计:\n{df.describe(include='all').to_string()}",
    ]
    return "\n".join(info_lines)


def get_column_names(file_path: str) -> list:
    """获取数据列名列表"""
    df = _load_data(file_path)
    return list(df.columns)


def get_numeric_columns(file_path: str) -> list:
    """获取数值类型的列名"""
    df = _load_data(file_path)
    return list(df.select_dtypes(include=['number']).columns)


def get_categorical_columns(file_path: str) -> list:
    """获取分类类型的列名"""
    df = _load_data(file_path)
    return list(df.select_dtypes(include=['object', 'category']).columns)


def clear_cache():
    """清除数据缓存"""
    _data_cache.clear()
