"""
数据分析工具
Agent 通过这些工具进行统计分析和数据探索
"""
import pandas as pd
import numpy as np
from tools.data_tools import _load_data


def describe_data(file_path: str) -> str:
    """
    生成数据描述性统计报告
    类似 df.describe() 的增强版

    参数:
        file_path: 数据文件路径
    返回:
        描述统计结果
    """
    df = _load_data(file_path)
    stats = df.describe(include='all')
    return stats.to_string()


def detect_missing_values(file_path: str) -> str:
    """
    检测缺失值：统计每列的缺失数量和比例

    这是数据质量检测的核心工具

    返回格式为 JSON，方便 Agent 解析
    """
    df = _load_data(file_path)
    missing = pd.DataFrame({
        'column': df.columns,
        'missing_count': df.isnull().sum().values,
        'missing_rate': (df.isnull().sum() / len(df)).values
    })
    missing = missing[missing['missing_count'] > 0].sort_values('missing_rate', ascending=False)
    return missing.to_json(orient='records', force_ascii=False)


def detect_duplicates(file_path: str) -> str:
    """检测重复行数量"""
    df = _load_data(file_path)
    dup_count = df.duplicated().sum()
    return f"重复行数: {dup_count}"


def detect_outliers(file_path: str, column: str = None) -> str:
    """
    使用 IQR 方法检测异常值
    IQR = Q3 - Q1
    异常值范围: < Q1-1.5*IQR 或 > Q3+1.5*IQR

    参数:
        file_path: 数据文件路径
        column: 指定列名（可选，不指定则检测所有数值列）
    """
    df = _load_data(file_path)
    numeric_cols = list(df.select_dtypes(include=['number']).columns)
    if column:
        numeric_cols = [column] if column in numeric_cols else []

    results = []
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        results.append({
            'column': col,
            'Q1': round(q1, 2),
            'Q3': round(q3, 2),
            'IQR': round(iqr, 2),
            'lower_bound': round(lower, 2),
            'upper_bound': round(upper, 2),
            'outlier_count': len(outliers),
            'outlier_rate': round(len(outliers) / len(df), 4)
        })

    return pd.DataFrame(results).to_json(orient='records', force_ascii=False)


def correlation_matrix(file_path: str) -> str:
    """
    计算数值列之间的相关性矩阵
    用于发现变量之间的线性关系

    返回:
        相关性矩阵（JSON 格式）
    """
    df = _load_data(file_path)
    numeric_df = df.select_dtypes(include=['number'])
    corr = numeric_df.corr()
    return corr.to_json(force_ascii=False)


def groupby_analysis(file_path: str, group_col: str, value_col: str, agg_func: str = "mean") -> str:
    """
    分组聚合分析

    参数:
        file_path: 数据文件路径
        group_col: 分组列名
        value_col: 聚合列名
        agg_func: 聚合函数 (mean, sum, count, min, max)

    返回:
        分组聚合结果
    """
    df = _load_data(file_path)
    if group_col not in df.columns:
        return f"错误: 列 '{group_col}' 不存在。可用列: {list(df.columns)}"
    if value_col not in df.columns:
        return f"错误: 列 '{value_col}' 不存在。可用列: {list(df.columns)}"

    grouped = df.groupby(group_col)[value_col].agg(agg_func).sort_values(ascending=False)
    return grouped.to_string()
